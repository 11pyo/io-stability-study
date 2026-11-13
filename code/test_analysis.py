"""Synthetic-data tests of the analysis pipeline (no real tables are read)."""

import numpy as np
import pytest

import analysis as a
import iomodel as m


def table(year, Z, x):
    n = len(x)
    return m.Table(year, tuple(f"{i + 1:02d}" for i in range(n)), tuple(f"s{i}" for i in range(n)),
                   np.array(Z, float), np.array(x, float))


def world(kind, seed, years, n=8):
    """A basis in which one model's coefficients are fixed and its exogenous vector moves."""
    rng = np.random.default_rng(seed)
    C = rng.uniform(0.0, 0.08, (n, n))
    inv = np.linalg.inv(np.eye(n) - C)
    out = {}
    e = rng.uniform(20, 60, n)
    for y in years:
        e = e * rng.uniform(0.9, 1.25, n)
        Cy = C * rng.uniform(0.995, 1.005, (n, n))      # small coefficient noise keeps every ratio finite
        inv = np.linalg.inv(np.eye(n) - Cy)
        if kind == "leontief":
            x = inv @ e
            out[y] = table(y, Cy * x[None, :], x)
        else:
            x = e @ inv
            out[y] = table(y, Cy * x[:, None], x)
    return out


@pytest.fixture(autouse=True)
def few_draws(monkeypatch):
    monkeypatch.setattr(a, "BOOT_DRAWS", 200)


def test_leontief_world_gives_exact_leontief_and_positive_r():
    t = {"2015": world("leontief", 1, a.BASES["2015"]), "2020": world("leontief", 2, a.BASES["2020"])}
    out = a.run_variant(t, energy_excluded=False, with_secondary=True)
    assert out["pooled"]["wape_x_leontief"] < 2e-3 and out["pooled"]["wape_z_leontief"] < 5e-3
    assert out["pooled"]["wape_x_ghosh"] > 5 * out["pooled"]["wape_x_leontief"]
    assert out["interval90"]["H1_r"][0] > 0          # Leontief more accurate, interval above zero
    assert out["pooled"]["wape_x_DL"] > out["pooled"]["wape_x_leontief"]


def test_ghosh_world_is_the_mirror_image():
    t = {"2015": world("ghosh", 3, a.BASES["2015"]), "2020": world("ghosh", 4, a.BASES["2020"])}
    out = a.run_variant(t, energy_excluded=False, with_secondary=False)
    assert out["pooled"]["wape_x_ghosh"] < 2e-3 and out["pooled"]["wape_z_ghosh"] < 5e-3
    assert out["interval90"]["H1_r"][1] < 0


def test_pooled_wape_is_ratio_of_sums_and_matches_manual():
    t = {"2015": world("leontief", 5, a.BASES["2015"]), "2020": world("ghosh", 6, a.BASES["2020"])}
    comps = {b: a.transition_components(t[b], a.BASES[b]) for b in t}
    sc = a.Scorer(comps, {b: np.ones(8) for b in t})
    ones = {b: np.ones(8) for b in t}
    num = den = 0.0
    for b in t:
        ys = a.BASES[b]
        for y0, y1 in zip(ys[:-1], ys[1:]):
            h = m.hindcasts(t[b][y0], t[b][y1].f, t[b][y1].w)
            num += np.abs(h["ghosh"] - t[b][y1].x).sum()
            den += t[b][y1].x.sum()
    assert sc.wape_x("ghosh", sc.all, ones) == pytest.approx(num / den, rel=1e-12)
    assert len(sc.all) == 8 and sum("t3" in comps[b][k] for b in comps for k in comps[b]) == 6


def test_bootstrap_is_reproducible_and_mask_removes_sectors():
    t = {"2015": world("leontief", 7, a.BASES["2015"]), "2020": world("ghosh", 8, a.BASES["2020"])}
    o1 = a.run_variant(t, energy_excluded=False, with_secondary=False)
    o2 = a.run_variant(t, energy_excluded=False, with_secondary=False)
    assert o1["interval90"] == o2["interval90"]
    o3 = a.run_variant(t, energy_excluded=True, with_secondary=False)      # codes 06 exists among 01..08
    assert o3["pooled"]["wape_x_ghosh"] != o1["pooled"]["wape_x_ghosh"]


def test_ras_reproduces_target_margins_and_is_identity_when_already_matching():
    rng = np.random.default_rng(9)
    z0, z1 = rng.uniform(1, 5, (6, 6)), rng.uniform(1, 5, (6, 6))
    z = a.ras(z0, z1.sum(axis=1), z1.sum(axis=0))
    np.testing.assert_allclose(z.sum(axis=1), z1.sum(axis=1), rtol=1e-7)
    np.testing.assert_allclose(z.sum(axis=0), z1.sum(axis=0), rtol=1e-7)
    np.testing.assert_allclose(a.ras(z1, z1.sum(axis=1), z1.sum(axis=0)), z1, rtol=1e-12)


def test_deflation_keeps_allocation_coefficients_and_identities():
    t = world("leontief", 10, a.BASES["2015"])
    rng = np.random.default_rng(11)
    price = {y: rng.uniform(0.7, 1.4, 8) for y in t}
    r = a.deflate(t, price)
    for y in t:
        _, B0 = m.coefficients(t[y])
        A1, B1 = m.coefficients(r[y])
        np.testing.assert_allclose(B1, B0, rtol=1e-12)
        A0, _ = m.coefficients(t[y])
        np.testing.assert_allclose(A1, A0 * price[y][None, :] / price[y][:, None], rtol=1e-12)
        np.testing.assert_allclose(r[y].Z.sum(axis=1) + r[y].f, r[y].x)


def test_spearman_handles_ties_and_perfect_order():
    assert a._spearman(np.array([1.0, 2.0, 3.0]), np.array([10.0, 20.0, 30.0])) == pytest.approx(1.0)
    assert a._spearman(np.array([1.0, 1.0, 2.0]), np.array([3.0, 3.0, 1.0])) == pytest.approx(-1.0)


# --------------------------------------------------
# Security Checklist
# Applied:
#   - Leftover debug code: synthetic data only; bootstrap count reduced inside the tests only (Category 6)
# Not Applied:
#   - [WARN] Authentication: not applicable - offline unit tests
# --------------------------------------------------
