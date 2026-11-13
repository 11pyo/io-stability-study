"""
Core definitions for the pre-registered study (PREREGISTRATION.md, sections 2 and 4).

Reads one Bank of Korea domestic transactions table and provides the Leontief and Ghosh hindcasts,
the baselines and the per-sector error components. Pure functions; no file is written here.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np

import xlsx_lite

FLOW_HINT = "국산거래표"
OUTPUT_COL = "9290"
FD_TOTAL_COL = "9190"
INTERMEDIATE_TOTAL_COL = "9090"
IDENTITY_TOL = 1e-6
# [SECURE] Whitelist pattern for sector codes read from untrusted workbooks (Category 1)
_SECTOR = re.compile(r"^\d{2,3}$")


@dataclass(frozen=True)
class Table:
    year: int
    codes: tuple[str, ...]
    names: tuple[str, ...]
    Z: np.ndarray          # domestic intermediate flows, rows sell, columns buy
    x: np.ndarray          # total output

    @property
    def f(self) -> np.ndarray:          # domestic final demand, by identity
        return self.x - self.Z.sum(axis=1)

    @property
    def w(self) -> np.ndarray:          # primary inputs (value added + imported intermediates), by identity
        return self.x - self.Z.sum(axis=0)


def _code(v) -> str:
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return str(v).strip()


def _num(v) -> float:
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise ValueError("Non-numeric cell in the flow block.")
    return float(v)


def parse_table(rows: list[tuple], year: int) -> Table:
    """Parse the rows of a domestic transactions sheet (header row holds the column codes)."""
    header_idx = next((i for i, r in enumerate(rows[:20]) if OUTPUT_COL in [_code(v) for v in r]), None)
    if header_idx is None:
        raise ValueError("Header row with column codes not found.")
    header = [_code(v) for v in rows[header_idx]]
    col_of = {}
    for j, c in enumerate(header):
        if c and c not in col_of:
            col_of[c] = j
    sector_cols = [(c, j) for c, j in col_of.items() if _SECTOR.fullmatch(c)]
    codes = tuple(c for c, _ in sector_cols)
    row_of, names = {}, {}
    for r in rows[header_idx + 1:]:
        c = _code(r[0]) if r else ""
        if c in col_of and _SECTOR.fullmatch(c) and c not in row_of:
            row_of[c] = r
            names[c] = _code(r[1])
    if set(row_of) != set(codes) or len(codes) < 10:
        raise ValueError("Row and column sector codes do not match.")
    n = len(codes)
    Z = np.empty((n, n))
    x = np.empty(n)
    fd = np.empty(n)
    for a, ci in enumerate(codes):
        r = row_of[ci]
        for b, (_, j) in enumerate(sector_cols):
            Z[a, b] = _num(r[j])
        x[a] = _num(r[col_of[OUTPUT_COL]])
        fd[a] = _num(r[col_of[FD_TOTAL_COL]])
    # [SECURE] Accounting identity check - a misread or damaged table is rejected (Category 1)
    resid = np.abs(Z.sum(axis=1) + fd - x) / np.maximum(np.abs(x), 1.0)
    if float(resid.max()) > IDENTITY_TOL:
        raise ValueError(f"Row identity violated (max relative residual {resid.max():.2e}).")
    return Table(year, codes, tuple(names[c] for c in codes), Z, x)


def load_table(path: Path, year: int) -> Table:
    sheets = [s for s in xlsx_lite.sheet_names(path) if FLOW_HINT in s]
    if len(sheets) != 1:
        raise ValueError("Domestic transactions sheet not found uniquely.")
    return parse_table(xlsx_lite.read_sheets(path, sheets)[sheets[0]], year)


def restrict(t: Table, keep: np.ndarray) -> Table:
    """
    Drop sectors (boolean mask) by removing their rows and columns of Z. Output x is kept, so flows to and
    from dropped sectors move into f and w through the identities - both identities still hold exactly.
    """
    idx = np.flatnonzero(keep)
    return Table(t.year, tuple(t.codes[i] for i in idx), tuple(t.names[i] for i in idx),
                 t.Z[np.ix_(idx, idx)], t.x[idx])


def coefficients(t: Table) -> tuple[np.ndarray, np.ndarray]:
    if np.any(t.x <= 0):
        raise ValueError("Output must be positive for every retained sector.")
    A = t.Z / t.x[None, :]          # input coefficients: column j divided by x_j
    B = t.Z / t.x[:, None]          # allocation coefficients: row i divided by x_i
    return A, B


def _inverse(M: np.ndarray) -> np.ndarray:
    n = M.shape[0]
    # [SECURE] Stability check before inversion - an explosive coefficient matrix is rejected (Category 1)
    if float(np.max(np.abs(np.linalg.eigvals(M)))) >= 1.0:
        raise ValueError("Coefficient matrix is not productive (spectral radius >= 1).")
    return np.linalg.inv(np.eye(n) - M)


def hindcasts(t0: Table, f1: np.ndarray, w1: np.ndarray) -> dict[str, np.ndarray]:
    """Output of t+1 implied by the structure of t and the given exogenous vectors (T2 / T3)."""
    A, B = coefficients(t0)
    return {
        "leontief": _inverse(A) @ f1,
        "ghosh": w1 @ _inverse(B),
        "direct_demand": t0.x + f1 - t0.f,
        "direct_supply": t0.x + w1 - t0.w,
    }


def stability_components(t0: Table, t1: Table) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """
    T1: per-sector numerators and denominators of WAPE_Z. Cell errors are attributed to the ROW (selling)
    sector for both models so that the same resampling unit serves both.
    """
    A, B = coefficients(t0)
    z_l = A * t1.x[None, :]
    z_g = B * t1.x[:, None]
    den = t1.Z.sum(axis=1)
    return {"leontief": (np.abs(z_l - t1.Z).sum(axis=1), den),
            "ghosh": (np.abs(z_g - t1.Z).sum(axis=1), den)}


# --------------------------------------------------
# Security Checklist
# Applied:
#   - Input validation: sector-code whitelist, numeric cells only, row/column code match, accounting
#     identity check, positive output, productive coefficient matrix (Category 1)
#   - Untrusted workbooks: read through the value-only reader (no formulas, size caps) (Category 5)
# Not Applied:
#   - [WARN] Integrity: file hashes are checked by the calling script against the provenance record, not here
# --------------------------------------------------
