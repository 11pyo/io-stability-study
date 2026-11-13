"""
Runs the pre-registered analysis (PREREGISTRATION.md, commit da90baf) and writes results/results.json.

Usage: python -B analysis.py <panel data dir> <ppi csv> <results dir>
Nothing is tuned here: every constant comes from the pre-registration.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

import numpy as np

import iomodel as m

BASES = {"2015": (2015, 2016, 2017, 2018, 2019), "2020": (2020, 2021, 2022, 2023, 2024)}
LEVELS = {"83": "통합중분류", "165": "통합소분류"}
P_SET = ("2020-21", "2021-22")
P_STAR = ("2021-22",)
O_STAR = ("2016-17", "2017-18", "2018-19", "2022-23", "2023-24")
ENERGY_83 = ("06", "16", "45", "46")
BOOT_DRAWS = 10000
BOOT_SEED = 20261113
TINY_SHARE = 0.0005
RAS_TOL, RAS_MAX_ITER = 1e-9, 1000
COMPILATION_FACTOR = 0.25
T2_METHODS = ("leontief", "ghosh", "N", "U", "DL", "DG")
T3_METHODS = ("leontief", "ghosh", "T", "N")
T1_METHODS = ("leontief", "ghosh", "ras")


def tkey(y0: int) -> str:
    return f"{y0}-{str(y0 + 1)[2:]}"


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    # [SECURE] Context manager guarantees the handle is released (Category 5)
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def find_file(panel: Path, year: int, level_word: str) -> Path:
    hits = [p for p in panel.glob("*.xlsx") if str(year) in p.name and level_word in p.name]
    if len(hits) != 1:
        raise ValueError(f"Expected one workbook for {year} {level_word}, found {len(hits)}.")
    return hits[0]


def load_basis(panel: Path, years: tuple[int, ...], level_word: str, prov: str) -> tuple[dict[int, m.Table], dict]:
    tables = {}
    for y in years:
        p = find_file(panel, y, level_word)
        # [SECURE] Integrity check against the provenance record before parsing (Category 5)
        if sha256_of(p) not in prov:
            raise ValueError(f"{p.name}: SHA-256 not in the provenance record.")
        tables[y] = m.load_table(p, y)
    codes = tables[years[0]].codes
    if any(t.codes != codes for t in tables.values()):
        raise ValueError("Sector codes differ within a basis.")
    keep = np.all([t.x > 0 for t in tables.values()], axis=0)
    info = {"n_sectors": int(len(codes)), "dropped_nonpositive_output": [codes[i] for i in np.flatnonzero(~keep)]}
    if not keep.all():
        tables = {y: m.restrict(t, keep) for y, t in tables.items()}
    info["negative_f"] = {str(y): int((t.f < 0).sum()) for y, t in tables.items()}
    info["negative_w"] = {str(y): int((t.w < 0).sum()) for y, t in tables.items()}
    return tables, info


def deflate(tables: dict[int, m.Table], price: dict[int, np.ndarray]) -> dict[int, m.Table]:
    """Robustness 5: rows of Z and x divided by the selling sector's price index (2020 = 1)."""
    out = {}
    for y, t in tables.items():
        p = price[y]
        if np.any(~np.isfinite(p)) or np.any(p <= 0):
            raise ValueError("Price indices must be finite and positive.")
        out[y] = m.Table(y, t.codes, t.names, t.Z / p[:, None], t.x / p)
    return out


def load_prices(ppi_csv: Path, concordance: Path, codes: tuple[str, ...], years: tuple[int, ...]) -> dict[int, np.ndarray]:
    with open(concordance, encoding="utf-8", newline="") as f:
        cmap = {r["io_code"]: r["ppi_item"] for r in csv.DictReader(l for l in f if not l.startswith("#"))}
    with open(ppi_csv, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    head = rows[0]
    first = {}
    for r in rows[1:]:
        first.setdefault(r[1].strip(), r)
    out = {}
    for y in years:
        col = head.index(str(y))
        vals = []
        for c in codes:
            if c not in cmap or cmap[c] not in first:
                raise ValueError(f"No price index for sector {c}.")
            vals.append(float(first[cmap[c]][col].replace(",", "")) / 100.0)
        out[y] = np.array(vals)
    return out


def ras(z0: np.ndarray, row_target: np.ndarray, col_target: np.ndarray) -> np.ndarray:
    """Biproportional adjustment of z0 to the given margins."""
    z = z0.copy()
    # [SECURE] Bounded iteration (Category 3)
    for _ in range(RAS_MAX_ITER):
        rs = z.sum(axis=1)
        z *= np.divide(row_target, rs, out=np.ones_like(rs), where=rs > 0)[:, None]
        cs = z.sum(axis=0)
        z *= np.divide(col_target, cs, out=np.ones_like(cs), where=cs > 0)[None, :]
        err = max(np.max(np.abs(z.sum(axis=1) - row_target)), np.max(np.abs(z.sum(axis=0) - col_target)))
        if err <= RAS_TOL * max(1.0, float(row_target.sum())):
            break
    return z


def transition_components(tables: dict[int, m.Table], years: tuple[int, ...]) -> dict[str, dict]:
    """Per-sector arrays for every transition of one basis. Models are solved once, here."""
    comp = {}
    for i, y0 in enumerate(years[:-1]):
        t0, t1 = tables[y0], tables[years[i + 1]]
        h = m.hindcasts(t0, t1.f, t1.w)
        pred = {"leontief": h["leontief"], "ghosh": h["ghosh"], "N": t0.x.copy(),
                "U": t0.x * (t1.x.sum() / t0.x.sum()), "DL": h["direct_demand"], "DG": h["direct_supply"]}
        s = m.stability_components(t0, t1)
        zr = ras(t0.Z, t1.Z.sum(axis=1), t1.Z.sum(axis=0))
        entry = {
            "x0": t0.x, "x1": t1.x,
            "t2": {k: np.abs(v - t1.x) for k, v in pred.items()},
            "t2_pred": pred,
            "t1_num": {"leontief": s["leontief"][0], "ghosh": s["ghosh"][0], "ras": np.abs(zr - t1.Z).sum(axis=1)},
            "t1_den": s["leontief"][1],
            "share0": t0.x / t0.x.sum(),
        }
        if i >= 1:
            tm = tables[years[i - 1]]
            h3 = m.hindcasts(t0, 2 * t0.f - tm.f, 2 * t0.w - tm.w)
            pred3 = {"leontief": h3["leontief"], "ghosh": h3["ghosh"], "T": 2 * t0.x - tm.x, "N": t0.x.copy()}
            entry["t3"] = {k: np.abs(v - t1.x) for k, v in pred3.items()}
        comp[tkey(y0)] = entry
    return comp


def _spearman(a: np.ndarray, b: np.ndarray) -> float:
    def ranks(v):
        order = np.argsort(v, kind="mergesort")
        r = np.empty(len(v))
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
                j += 1
            r[order[i:j + 1]] = (i + j) / 2.0 + 1.0
            i = j + 1
        return r
    ra, rb = ranks(a), ranks(b)
    if ra.std() == 0 or rb.std() == 0:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


class Scorer:
    """Pooled statistics from per-sector components; `counts` are resampling multiplicities per basis."""

    def __init__(self, comps: dict[str, dict[str, dict]], score_mask: dict[str, np.ndarray]):
        self.comps = comps                    # basis -> transition -> arrays
        self.mask = score_mask                # basis -> 0/1 array (sectors that enter the scores)
        self.where = {t: b for b, d in comps.items() for t in d}
        self.all = tuple(sorted(self.where))

    def wape_x(self, method: str, ts, counts, block="t2") -> float:
        num = den = 0.0
        for t in ts:
            b = self.where[t]
            e = self.comps[b][t]
            c = counts[b] * self.mask[b]
            num += float(c @ e[block][method])
            den += float(c @ e["x1"])
        return num / den

    def wape_z(self, method: str, ts, counts) -> float:
        num = den = 0.0
        for t in ts:
            b = self.where[t]
            e = self.comps[b][t]
            c = counts[b] * self.mask[b]
            num += float(c @ e["t1_num"][method])
            den += float(c @ e["t1_den"])
        return num / den

    def r(self, ts, counts) -> float:
        return float(np.log(self.wape_x("ghosh", ts, counts) / self.wape_x("leontief", ts, counts)))

    def growth_errors(self, method: str, ts, index) -> np.ndarray:
        out = []
        for t in ts:
            b = self.where[t]
            e = self.comps[b][t]
            ok = (e["share0"] >= TINY_SHARE) & (self.mask[b] > 0)
            ge = np.abs(e["t2_pred"][method] - e["x1"]) / e["x0"] * 100.0
            idx = index[b]
            out.append(ge[idx][ok[idx]])
        return np.concatenate(out)

    def statistics(self, counts) -> dict[str, float]:
        A = self.all
        O = tuple(t for t in A if t not in P_SET)
        Ostar = tuple(t for t in O_STAR if t in A)
        t3 = tuple(t for t in A if "t3" in self.comps[self.where[t]][t])
        s = {"H1_r": self.r(A, counts),
             "H2_d2": self.r(O, counts) - self.r(P_SET, counts),
             "H2b_d2star": self.r(Ostar, counts) - self.r(P_STAR, counts),
             "H4_leontief": float(np.log(self.wape_x("DL", A, counts) / self.wape_x("leontief", A, counts))),
             "H4_ghosh": float(np.log(self.wape_x("DG", A, counts) / self.wape_x("ghosh", A, counts)))}
        for mdl in ("leontief", "ghosh"):
            s[f"H3_{mdl}"] = float(np.log(self.wape_z(mdl, P_SET, counts) / self.wape_z(mdl, O, counts)))
            s[f"H3b_{mdl}"] = float(np.log(self.wape_z(mdl, P_STAR, counts) / self.wape_z(mdl, Ostar, counts)))
            s[f"H5_{mdl}"] = float(np.log(self.wape_x("T", t3, counts, "t3") / self.wape_x(mdl, t3, counts, "t3")))
            s[f"gate_U_minus_{mdl}"] = self.wape_x("U", A, counts) - self.wape_x(mdl, A, counts)
        no24 = tuple(t for t in A if t != "2023-24")
        s["R6_H1_r"] = self.r(no24, counts)
        s["R6_H2_d2"] = self.r(tuple(t for t in no24 if t not in P_SET), counts) - self.r(P_SET, counts)
        for b in self.comps:
            s[f"R4_H1_r_basis{b}"] = self.r(tuple(self.comps[b]), counts)
        return s

    def secondary(self, index) -> dict[str, float]:
        A = self.all
        O = tuple(t for t in A if t not in P_SET)
        med = lambda mth, ts: float(np.median(self.growth_errors(mth, ts, index)))
        return {"R3_H1_log_ratio_of_medians": float(np.log(med("ghosh", A) / med("leontief", A))),
                "R3_H2_d2_medians": float(np.log(med("ghosh", O) / med("leontief", O))
                                          - np.log(med("ghosh", P_SET) / med("leontief", P_SET)))}


def bootstrap(sc: Scorer, with_secondary: bool) -> dict[str, list[float]]:
    # Statistical resampling, seeded for reproducibility; not a security decision.
    rng = np.random.default_rng(BOOT_SEED)
    sizes = {b: len(next(iter(d.values()))["x1"]) for b, d in sc.comps.items()}
    draws: dict[str, list[float]] = {}
    for _ in range(BOOT_DRAWS):
        index = {b: rng.integers(0, n, n) for b, n in sizes.items()}
        counts = {b: np.bincount(index[b], minlength=sizes[b]).astype(float) for b in sizes}
        st = sc.statistics(counts)
        if with_secondary:
            st.update(sc.secondary(index))
        for k, v in st.items():
            draws.setdefault(k, []).append(v)
    return {k: [float(np.percentile(v, 5)), float(np.percentile(v, 95))] for k, v in draws.items()}


def describe(sc: Scorer) -> dict:
    ones = {b: np.ones(len(next(iter(d.values()))["x1"])) for b, d in sc.comps.items()}
    ident = {b: np.arange(len(v)) for b, v in ones.items()}
    per = {}
    for t in sc.all:
        e = sc.comps[sc.where[t]][t]
        row = {f"wape_x_{k}": sc.wape_x(k, (t,), ones) for k in T2_METHODS}
        row.update({f"wape_z_{k}": sc.wape_z(k, (t,), ones) for k in T1_METHODS})
        row["r"] = sc.r((t,), ones)
        if "t3" in e:
            row.update({f"t3_wape_x_{k}": sc.wape_x(k, (t,), ones, "t3") for k in T3_METHODS})
        g_act = e["x1"] / e["x0"] - 1
        for k in ("leontief", "ghosh"):
            row[f"spearman_{k}"] = _spearman(e["t2_pred"][k] / e["x0"] - 1, g_act)
            ge = sc.growth_errors(k, (t,), ident)
            row[f"growth_abs_err_median_{k}"] = float(np.median(ge))
            row[f"growth_abs_err_mean_{k}"] = float(np.mean(ge))
        row["n_tiny_excluded"] = int((e["share0"] < TINY_SHARE).sum())
        per[t] = row
    A = sc.all
    pooled = {f"wape_x_{k}": sc.wape_x(k, A, ones) for k in T2_METHODS}
    pooled.update({f"wape_z_{k}": sc.wape_z(k, A, ones) for k in T1_METHODS})
    ext = tuple(t for t in O_STAR if t in A)
    pooled["compilation"] = {k: sc.wape_z(k, ext, ones) for k in T1_METHODS}
    order = sorted(A, key=lambda t: per[t]["r"])
    return {"per_transition": per, "pooled": pooled, "point": {**sc.statistics(ones), **sc.secondary(ident)},
            "rank_condition": {"order_by_r": order, "holds": set(order[:2]) == set(P_SET)},
            "spearman_median": {k: float(np.median([per[t][f"spearman_{k}"] for t in A])) for k in ("leontief", "ghosh")}}


def run_variant(tables: dict[str, dict[int, m.Table]], energy_excluded: bool, with_secondary: bool) -> dict:
    comps = {b: transition_components(tables[b], BASES[b]) for b in tables}
    mask = {}
    for b, tb in tables.items():
        codes = next(iter(tb.values())).codes
        mask[b] = np.array([0.0 if (energy_excluded and c in ENERGY_83) else 1.0 for c in codes])
    sc = Scorer(comps, mask)
    out = describe(sc)
    out["interval90"] = bootstrap(sc, with_secondary)
    return out


def main(argv) -> int:
    if len(argv) != 4:
        print("usage: analysis.py <panel data dir> <ppi csv> <results dir>")
        return 2
    panel, ppi_csv, res_dir = Path(argv[1]), Path(argv[2]), Path(argv[3])
    if not panel.is_dir() or not ppi_csv.is_file() or not res_dir.is_dir():
        print("Input folder, price file or results folder not found.")
        return 2
    try:
        prov = (panel / "PROVENANCE_ecos_panel.txt").read_text(encoding="utf-8")
        out = {"preregistration_commit": "da90baf", "inputs": {}}
        t83, info83 = {}, {}
        for b, years in BASES.items():
            t83[b], info83[b] = load_basis(panel, years, LEVELS["83"], prov)
        out["inputs"]["83"] = info83
        out["main_83_current_prices"] = run_variant(t83, energy_excluded=False, with_secondary=True)
        out["R2_energy_excluded"] = run_variant(t83, energy_excluded=True, with_secondary=False)
        conc = Path(__file__).resolve().parent.parent / "data" / "ppi_to_io83.csv"
        real = {}
        for b, years in BASES.items():
            codes = next(iter(t83[b].values())).codes
            real[b] = deflate(t83[b], load_prices(ppi_csv, conc, codes, years))
        out["inputs"]["83_constant_prices"] = {b: {"negative_f": {str(y): int((t.f < 0).sum()) for y, t in real[b].items()},
                                                    "negative_w": {str(y): int((t.w < 0).sum()) for y, t in real[b].items()}}
                                               for b in real}
        out["R5_constant_prices"] = run_variant(real, energy_excluded=False, with_secondary=False)
        t165, info165 = {}, {}
        for b, years in BASES.items():
            t165[b], info165[b] = load_basis(panel, years, LEVELS["165"], prov)
        out["inputs"]["165"] = info165
        out["R1_165_sectors"] = run_variant(t165, energy_excluded=False, with_secondary=False)
    except (OSError, ValueError, KeyError) as e:
        # [SECURE] Short reason, no stack trace for expected input problems (Category 4)
        print(f"Analysis stopped: {e}", file=sys.stderr)
        return 1
    fd, tmp = tempfile.mkstemp(prefix=".results.", suffix=".tmp", dir=res_dir)
    try:
        # [SECURE] Atomic write of the results file (Category 3)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1, sort_keys=True)
        os.replace(tmp, res_dir / "results.json")
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise
    print("results written:", (res_dir / "results.json").name, "sha256", sha256_of(res_dir / "results.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))


# --------------------------------------------------
# Security Checklist
# Applied:
#   - Integrity: every workbook is checked against the provenance record before parsing (Category 5)
#   - Input validation: arguments must exist; one workbook per year and level; identical sector codes within
#     a basis; positive finite prices; accounting identities checked in iomodel (Category 1)
#   - Bounded loops: fixed bootstrap count, capped RAS iterations (Category 3)
#   - Error handling: short messages and non-zero exit for expected problems; atomic output (Category 3, 4)
# Not Applied:
#   - [WARN] Improper random value: numpy default_rng on purpose - seeded statistical resampling
#   - [WARN] Authentication: not applicable - local analysis script
# --------------------------------------------------
