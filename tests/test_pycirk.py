#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `pycirk` package."""

import pytest
import pycirk



@pytest.fixture
def test():
    t = pycirk.Launch(test=True)
    return t

def results():
    return test().all_results()

if __name__ == "__main__":
    assert(results())
