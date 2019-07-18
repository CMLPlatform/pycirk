#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `pycirk` package."""

import pytest
import pycirk


@pytest.fixture
def initialise_method():
    return(pycirk.Launch("test"))

def test_all_results_method0():
    """Sample pytest test function with the pytest fixture as an argument."""
    return(initialise_method().all_results())

if __name__ == "__main__":
    assert(test_all_results_method0())
