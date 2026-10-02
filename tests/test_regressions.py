"""Regression tests on small synthetic matrices (no EXIOBASE download needed)."""

import numpy as np
import pandas as pd

from pycirk.make_scenarios import counterfactual_engine
from pycirk.make_secondary_flows import make_secondary
from pycirk.pycirk_settings import Settings

nan = np.nan


def intervention(**kw):
    base = dict(
        ide=1,
        i=np.array([0]),
        g=np.array([0]),
        i1=np.array([1]),
        g1=np.array([0]),
        kt1={"kt": nan, "kp": nan},
        kt2={"kt": nan, "kp": nan},
        at1=nan,
        at2=nan,
        swk=100.0,
        sk1=nan,
        sk2=nan,
        sk3=nan,
        sk4=nan,
    )
    base.update(kw)
    return base


def run(**kw):
    M = np.array([[10.0], [0.0]])
    return counterfactual_engine(M, intervention(**kw), subs=True).ravel()


def test_substitution_of_first_step_still_works():
    out = run(kt1={"kt": -50.0, "kp": 100.0}, sk1="x")
    assert np.allclose(out, [5, 5])


def test_substitution_of_second_step():
    out = run(kt2={"kt": -50.0, "kp": 100.0}, sk2="x")
    assert np.allclose(out, [5, 5])


def test_substitution_ignores_later_additive_change():
    out = run(kt1={"kt": -50.0, "kp": 100.0}, at1=2.0, sk1="x")
    assert np.allclose(out, [7, 5])


def test_make_secondary_keeps_product_balance():
    rng = np.random.default_rng(0)
    n_prod, n_ind = 200, 163
    secondary = np.array([57, 59, 85, 96, 100, 103, 105, 107, 109, 111, 113, 149]) + 1
    U = rng.random((n_prod, n_ind))
    Y = rng.random((n_prod, 7))
    U[secondary] = 0
    Y[secondary] = 0
    q = U.sum(1) + Y.sum(1)
    V = rng.random((n_prod, n_ind))
    V *= (q / V.sum(1))[:, None]
    V[secondary] = 0

    out = make_secondary({"V": pd.DataFrame(V), "U": pd.DataFrame(U), "Y": pd.DataFrame(Y)})

    supply = out["V"].to_numpy().sum(1)
    use = out["U"].to_numpy().sum(1) + out["Y"].to_numpy().sum(1)
    assert np.allclose(supply, use)


def test_method_label_matches_transformation():
    assert "TCm" in Settings(method=0).project_specs(test=True)["Method"]
    assert "MSCm" in Settings(method=1).project_specs(test=True)["Method"]


def test_io_cache_name_depends_on_settings():
    names = {
        Settings(method=m, make_secondary=s, aggregation=a).io_cache_file()
        for m in (0, 1)
        for s in (False, True)
        for a in (0, 1)
    }
    assert len(names) == 8
    # caches written before the make_secondary fix must not be picked up
    assert "data//mrIO_V3.3.sm.pkl" not in names
