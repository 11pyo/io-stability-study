"""Synthetic-data tests for iomodel (no real tables are read)."""

import numpy as np
import pytest

import iomodel as m


def make(year, Z, x):
    n = len(x)
    return m.Table(year, tuple(f"{i + 1:02d}" for i in range(n)), tuple(f"s{i}" for i in range(n)),
                   np.array(Z, float), np.array(x, float))


@pytest.fixture
def pair():
    rng = np.random.default_rng(1)
    n = 6
    x0 = rng.uniform(50, 150, n)
    Z0 = rng.uniform(0, 8, (n, n))
    t0 = make(2015, Z0, x0)
    x1 = x0 * rng.uniform(0.9, 1.2, n)
    Z1 = Z0 * rng.uniform(0.8, 1.3, (n, n))
    return t0, make(2016, Z1, x1)


def test_identities_hold(pair):
    t0, _ = pair
    np.testing.assert_allclose(t0.Z.sum(axis=1) + t0.f, t0.x)
    np.testing.assert_allclose(t0.Z.sum(axis=0) + t0.w, t0.x)


def test_same_year_hindcast_is_exact_for_both_models(pair):
    t0, _ = pair
    h = m.hindcasts(t0, t0.f, t0.w)
    np.testing.assert_allclose(h["leontief"], t0.x, rtol=1e-10)
    np.testing.assert_allclose(h["ghosh"], t0.x, rtol=1e-10)
    np.testing.assert_allclose(h["direct_demand"], t0.x)
    np.testing.assert_allclose(h["direct_supply"], t0.x)


def test_unchanged_coefficients_give_exact_next_year():
    # Leontief world: A fixed, final demand changes -> Leontief exact, Ghosh generally not.
    A = np.array([[0.1, 0.2, 0.0], [0.05, 0.1, 0.3], [0.2, 0.0, 0.1]])
    L = np.linalg.inv(np.eye(3) - A)
    f0, f1 = np.array([10.0, 20.0, 30.0]), np.array([14.0, 18.0, 33.0])
    x0, x1 = L @ f0, L @ f1
    t0, t1 = make(2015, A * x0[None, :], x0), make(2016, A * x1[None, :], x1)
    h = m.hindcasts(t0, t1.f, t1.w)
    np.testing.assert_allclose(h["leontief"], x1, rtol=1e-10)
    assert np.max(np.abs(h["ghosh"] - x1)) > 1e-3
    s = m.stability_components(t0, t1)
    assert s["leontief"][0].sum() < 1e-9 and s["ghosh"][0].sum() > 1e-3


def test_ghosh_world_is_symmetric_case():
    # Ghosh world: B fixed, primary inputs change -> Ghosh exact, Leontief generally not.
    B = np.array([[0.1, 0.2, 0.0], [0.05, 0.1, 0.3], [0.2, 0.0, 0.1]])
    G = np.linalg.inv(np.eye(3) - B)
    w0, w1 = np.array([10.0, 20.0, 30.0]), np.array([14.0, 18.0, 33.0])
    x0, x1 = w0 @ G, w1 @ G
    t0, t1 = make(2015, B * x0[:, None], x0), make(2016, B * x1[:, None], x1)
    h = m.hindcasts(t0, t1.f, t1.w)
    np.testing.assert_allclose(h["ghosh"], x1, rtol=1e-10)
    assert np.max(np.abs(h["leontief"] - x1)) > 1e-3
    s = m.stability_components(t0, t1)
    assert s["ghosh"][0].sum() < 1e-9 and s["leontief"][0].sum() > 1e-3


def test_transpose_symmetry(pair):
    # Swapping the roles of rows and columns swaps the two models exactly.
    t0, t1 = pair
    t0T, t1T = make(2015, t0.Z.T, t0.x), make(2016, t1.Z.T, t1.x)
    h, hT = m.hindcasts(t0, t1.f, t1.w), m.hindcasts(t0T, t1T.f, t1T.w)
    np.testing.assert_allclose(h["leontief"], hT["ghosh"], rtol=1e-10)
    np.testing.assert_allclose(h["ghosh"], hT["leontief"], rtol=1e-10)
    np.testing.assert_allclose(h["direct_demand"], hT["direct_supply"], rtol=1e-12)


def test_restrict_keeps_identities(pair):
    t0, _ = pair
    r = m.restrict(t0, np.array([True, False, True, True, False, True]))
    np.testing.assert_allclose(r.Z.sum(axis=1) + r.f, r.x)
    np.testing.assert_allclose(r.Z.sum(axis=0) + r.w, r.x)
    assert len(r.codes) == 4


def test_parse_rejects_broken_identity_and_text_cells():
    hdr = ("", "", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "9090", "9190", "9290")
    def row(i, vals, fd, x):
        return (f"{i:02d}", f"n{i}", *vals, sum(vals), fd, x)
    good = [("t",), hdr] + [row(i, [1.0] * 10, 5.0, 15.0) for i in range(1, 11)]
    t = m.parse_table(good, 2015)
    assert t.Z.shape == (10, 10) and np.allclose(t.x, 15.0)
    bad = [("t",), hdr] + [row(i, [1.0] * 10, 5.0, 16.0 if i == 3 else 15.0) for i in range(1, 11)]
    with pytest.raises(ValueError):
        m.parse_table(bad, 2015)
    txt = [("t",), hdr] + [row(i, [1.0] * 9 + ["x"] if i == 2 else [1.0] * 10, 5.0, 15.0) for i in range(1, 11)] \
        if False else None
    rows = [("t",), hdr] + [row(i, [1.0] * 10, 5.0, 15.0) for i in range(1, 11)]
    r2 = list(rows[3])
    r2[4] = "n/a"
    rows[3] = tuple(r2)
    with pytest.raises(ValueError):
        m.parse_table(rows, 2015)


def test_unproductive_matrix_rejected():
    t = make(2015, [[60.0, 50.0], [50.0, 60.0]], [100.0, 100.0])
    with pytest.raises(ValueError):
        m.hindcasts(t, t.f, t.w)


# --------------------------------------------------
# Security Checklist
# Applied:
#   - Input validation tests: broken identity, non-numeric cell, unproductive matrix (Category 1)
#   - Leftover debug code: synthetic data only (Category 6)
# Not Applied:
#   - [WARN] Authentication: not applicable - offline unit tests
# --------------------------------------------------
