#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `pycirk` package."""

import pytest
import pycirk


@pytest.fixture
def initialise_method_0():
    s = pycirk.Start(0, "test")
    return(s)

def initialise_method_1():
    s = pycirk.Start(1, "test")
    return(s)

def test_all_results_method0():
    """Sample pytest test function with the pytest fixture as an argument."""
    g = initialise_method_0().all_results()
    return(g)

def test_all_results_method1():
    """Sample pytest test function with the pytest fixture as an argument."""
    g = initialise_method_1().all_results()
    return(g)
# =============================================================================
# def test_save_everything():
#     """Sample pytest test function with the pytest fixture as an argument."""
#     g = response().save_everything()
#     return(g)
# =============================================================================


if __name__ == "__main__":
    assert(test_all_results_method0())
    assert(test_all_results_method1())
#    assert(test_save_everything())
