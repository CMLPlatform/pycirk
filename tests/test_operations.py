"""The vector rewrite and the scenario update must match the dense formulas."""

import numpy as np
import pytest

from pycirk.fundamental_operations import Operations as ops
from pycirk.transformation_methods import Transform

TOL = dict(rtol=1e-10, atol=1e-12)


@pytest.fixture(scope="module")
def system():
    n = 300
    rng = np.random.default_rng(1)
    A0 = rng.random((n, n)) * 0.5 / n
    y = rng.random(n)
    return A0, y, ops.IOT._factorize(A0.copy())


def changed(A0, rows=(), cols=()):
    A = A0.copy()
    A[list(rows), :] *= 0.7
    A[:, list(cols)] *= 1.3
    return A


def no_fallback(*args):
    raise AssertionError("the update fell back to a full solve")


@pytest.mark.parametrize(
    "rows, cols",
    [
        ((), ()),
        ((3, 40, 41), ()),
        ((), (5, 6, 200)),
        ((3, 40), (5, 6, 200)),  # steel row into everything + a column block
    ],
)
def test_update_matches_full_solve(system, monkeypatch, rows, cols):
    A0, y, lu0 = system
    A = changed(A0, rows, cols)
    expected = ops.IOT.x_solve(A, y)
    monkeypatch.setattr(ops.IOT, "x_solve", no_fallback)
    x = ops.IOT._x_update(A, y, A0.copy(), lu0)
    assert np.allclose(x, expected, **TOL)


def test_cover_contains_every_change(system):
    A0 = system[0]
    D = changed(A0, (3, 40), (5, 6, 200)) - A0
    R, C = ops.IOT._change_cover(D)
    outside = np.ones(D.shape, dtype=bool)
    outside[R] = False
    outside[:, C] = False
    assert not D[outside].any()
    assert len(R) + len(C) == 5


def test_large_change_falls_back_to_full_solve(system, monkeypatch):
    A0, y, lu0 = system
    A = changed(A0, range(0, len(A0), 2))
    expected = ops.IOT.x_solve(A, y)
    calls = []
    full_solve = ops.IOT.x_solve
    monkeypatch.setattr(ops.IOT, "x_solve", lambda *a: calls.append(1) or full_solve(*a))
    x = ops.IOT._x_update(A, y, A0.copy(), lu0, max_rank=10)
    assert calls == [1]
    assert np.allclose(x, expected, **TOL)


@pytest.mark.parametrize("helper", [
    ops.IOT.Z, ops.IOT.A, ops.IOT.B, ops.IOT.R, ops.IOT.bY, ops.IOT.RY,
    ops.PxP_ITA_TC.R, ops.PxP_ITA_MSC.R, ops.PxP_ITA_MSC.S,
])
def test_diagonal_matrix_arguments_still_work(helper):
    rng = np.random.default_rng(2)
    M, v = rng.random((3, 5)), rng.random(5)
    with pytest.warns(DeprecationWarning):
        out = helper(M, np.diag(v))
    assert np.allclose(out, M @ np.diag(v))


def dense_reference(S, method):
    """The pre-vector formulas, with explicit diagonal matrices."""
    V, U, Y = S["V"], S["U"], S["Y"]
    q, g = V.sum(1), V.sum(0)
    iq = np.diag(np.where(q != 0, 1 / np.where(q == 0, 1, q), 0))
    ig = np.diag(np.where(g != 0, 1 / np.where(g == 0, 1, g), 0))
    if method == "TC":
        T = ig @ V.T
        A = U @ T @ iq
        Z = U @ T  # TC scales by q, not by x
        B = lambda X: X @ T @ iq
    else:
        A = (U @ ig) @ (V.T @ iq)
        Z = None
        B = lambda X: (X @ ig) @ (V.T @ iq)
    x = np.linalg.inv(np.eye(len(A)) - A) @ Y.sum(1)
    Z = A @ np.diag(x) if Z is None else Z
    return {"A": A, "Z": Z, **{k: B(S[k]) @ np.diag(x) for k in "WERM"}}


@pytest.mark.parametrize("method", ["TC", "MSC"])
def test_transform_matches_dense_formulas(method):
    rng = np.random.default_rng(0)
    S = {
        k: rng.random(shape)
        for k, shape in {
            "V": (8, 6),
            "U": (8, 6),
            "Y": (8, 4),
            "W": (3, 6),
            "E": (2, 6),
            "R": (2, 6),
            "M": (2, 6),
            "YE": (2, 4),
            "YR": (2, 4),
            "YM": (2, 4),
        }.items()
    }
    S["U"] *= 0.1
    S["V"][2] = 0  # a product nobody supplies
    S.update({f"Cr_{k}_k": 1 for k in "ERMW"})
    expected = dense_reference(S, method)
    out = getattr(Transform(dict(S)), f"IOTpxpSTA_{method}m")()
    for k, v in expected.items():
        assert np.allclose(out[k], v, **TOL), k
