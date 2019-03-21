# -*- coding: utf-8 -*-
"""
Created on Tue Feb 7 16:29:23 2017

Description: Calculate baseline and scenarios in IOT

Scope: Modelling the Circular economy in EEIO


@author: Franco Donati
@institution: Leiden University CML
"""

# import warnings
import numpy as np
from pycirk.fundamental_operations import Operations as ops


class Organize_IO:
    """
    Creates an object out of IO dataset
    """
    def __init__(self, data):
        self.E = data["E"]
        self.RE = data["RE"]
        self.L = data["L"]
        self.S = data["S"]
        self.x = data["x"]
        self.A = data["A"]
        self.Y = data["Y"]

        self.RBe = data["RBe"]
        self.RBr = data["RBr"]
        self.RBm = data["RBm"]

        self.Be = data["Be"]
        self.Br = data["Br"]
        self.Bm = data["Bm"]

        # characterization factors for extensions
        self.CrBe_k = data["CrBe_k"]
        self.CrBr_k = data["CrBr_k"]
        self.CrBm_k = data["CrBm_k"]
        self.CrE_k = data["CrE_k"]

        self.ver_base = data["ver_base"]

        # Calculating intensity matrices for final demand extentions

        YBe_ = data["YBe"]
        YBr_ = data["YBr"]
        YBm_ = data["YBm"]

        diag_yj = np.diag(self.Y.sum(axis=0))

        _YBe = ops.IOT.FD_EXT(YBe_, diag_yj)
        _YBr = ops.IOT.FD_EXT(YBr_, diag_yj)
        _YBm = ops.IOT.FD_EXT(YBm_, diag_yj)

        self.YBe = _YBe["YB"]
        self.YBr = _YBr["YB"]
        self.YBm = _YBm["YB"]
        self.RYBe = _YBe["RYB"]
        self.RYBr = _YBr["RYB"]
        self.RYBm = _YBm["RYB"]

        # Characterized extensions
        self.CrBe = np.matmul(self.CrBe_k, self.Be)  # emissions ext
        self.CrBr = np.matmul(self.CrBr_k, self.Br)  # resource ext
        self.CrBm = np.matmul(self.CrBm_k, self.Bm)  # material ext
        self.CrE = np.matmul(self.CrE_k, self.E)  # factor inputs

        self.CrYBe = np.matmul(self.CrBe_k, self.YBe)  # emissions ext
        self.CrYBr = np.matmul(self.CrBr_k, self.YBr)  # resource ext
        self.CrYBm = np.matmul(self.CrBm_k, self.YBm)  # material ext
