"""The scenario update must agree with a full solve of (I - A) x = y."""

import numpy as np
import pytest

from pycirk.fundamental_operations import Operations as ops

n = 300
rng = np.random.default_rng(1)
A0 = rng.random((n, n)) * 0.5 / n
y = rng.random(n)
lu0 = ops.IOT.factorize(A0.copy())


def changed(rows=(), cols=()):
    A = A0.copy()
    A[list(rows), :] *= 0.7
    A[:, list(cols)] *= 1.3
    return A


@pytest.mark.parametrize(
    "rows, cols",
    [
        ((), ()),
        ((3, 40, 41), ()),
        ((), (5, 6, 200)),
        ((3, 40), (5, 6, 200)),  # steel row into everything + a column block
    ],
)
def test_update_matches_full_solve(rows, cols):
    A = changed(rows, cols)
    x = ops.IOT.x_update(A, y, A0.copy(), lu0)
    assert np.allclose(x, ops.IOT.x_solve(A, y), rtol=1e-12, atol=0)


def test_cover_is_small_for_mixed_change():
    R, C = ops.IOT.change_cover(changed((3, 40), (5, 6, 200)) - A0)
    assert len(R) + len(C) == 5


def test_large_change_falls_back_to_full_solve():
    A = changed(range(0, n, 2))
    x = ops.IOT.x_update(A, y, A0.copy(), lu0, max_rank=10)
    assert np.allclose(x, ops.IOT.x_solve(A, y), rtol=1e-12, atol=0)
