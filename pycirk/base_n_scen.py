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
from pandas import DataFrame as df
from pycirk.SUTops import SUTops as sops
from pycirk.apply_policy import Apply_policy
from pycirk.SUTtoIOT import basic_labels


class Base_n_scen:
    """
    Loads base data and assembles new tables (scenario) from the processed data
    """
    def __init__(self, data):
        """
        Baseline IOT
        """
        self.IOT = data

        self.E_ = data["E"]
        self.RE_ = data["RE"]
        self.L_ = data["L"]
        self.S_ = data["S"]
        self.x_ = data["x"]
        self.A_ = data["A"]
        self.Y_ = data["Y"]

        self.RBe_ = data["RBe"]
        self.RBr_ = data["RBr"]
        self.RBm_ = data["RBm"]

        self.Be_ = data["Be"]
        self.Br_ = data["Br"]
        self.Bm_ = data["Bm"]

        self.YBe_ = data["YBe"]
        self.YBr_ = data["YBr"]
        self.YBm_ = data["YBm"]
        self.ver_base = data["ver"]

        self.diag_yj = np.diag(self.Y.sum(axis=0))

        # Calculating intensity matrices for final demand extentions
        self._YBe = sops.IOT.FD_EXT(self.YBe, self.diag_yj)
        self._YBr = sops.IOT.FD_EXT(self.YBr, self.diag_yj)
        self._YBm = sops.IOT.FD_EXT(self.YBm, self.diag_yj)

        self.YBe_ = self._YBe["YB"]
        self.YBr_ = self._YBr["YB"]
        self.YBm_ = self._YBm["YB"]
        self.RYBe_ = self._YBe["RYB"]
        self.RYBr_ = self._YBr["RYB"]
        self.RYBm_ = self._YBm["RYB"]

        # Characterisation
        self.CrBe_ = np.matmul(self.SUTs.CrBe, self.Be)  # emissions ext
        self.CrBr_ = np.matmul(self.SUTs.CrBr, self.Br)  # resource ext
        self.CrBm_ = np.matmul(self.SUTs.CrBm, self.Bm)  # material ext
        self.CrE_ = np.matmul(self.SUTs.CrE, self.E)  # factor inputs

        self.CrYBe_ = np.matmul(self.SUTs.CrBe, self.YBe)  # emissions ext
        self.CrYBr_ = np.matmul(self.SUTs.CrBr, self.YBr)  # resource ext
        self.CrYBm_ = np.matmul(self.SUTs.CrBm, self.YBm)  # material ext

    def sceneIOT(self, scen_no, scen_file):
        """
        baseline IOT calculated with Technical Coefficient or
        Market coefficient method
        """

#        if scen_no in [0, "baseline", "base"]:
#            warnings.warn("You specified the baseline so no changes were made."
#                          "Baseline was returned. Possible scenarios [1,2,n]")
#            return(self.IOT)
#        else:

        ap = Apply_policy(scen_file)

        Y_ = self.Y_.copy(True)
        S_ = self.S_.copy(True)
        RE_ = self.RE_.copy(True)
        RBe_ = self.RBe_.copy(True)
        RBr_ = self.RBr_.copy(True)
        RBm_ = self.RBm_.copy(True)
        RYBe_ = self.RYBe_.copy(True)
        RYBr_ = self.RYBr_.copy(True)
        RYBm_ = self.RYBm_.copy(True)

        # Apply policy to economic matrices

        S_ = ap.apply_policy(scen_no, S_, "S")
        inv_diag_x = sops.inv(np.diag(sops.IOT.x(S_, Y_)))
        A_ = sops.IOT.A(S_, inv_diag_x)
        self.A = ap.apply_policy(scen_no, df(A_), "A")

        self.Y = ap.apply_policy(scen_no, Y_, "Y")
        self.RE = ap.apply_policy(scen_no, RE_, "RE")

        # Apply policy to intermediate extension coefficient matrices
        self.RBe = ap.apply_policy(scen_no, RBe_, "RBe")
        self.RBr = ap.apply_policy(scen_no, RBr_, "RBr")
        self.RBm = ap.apply_policy(scen_no, RBm_, "RBm")

        # Apply policy to  final demand extension coefficient matrices
        self.RYBe = ap.apply_policy(scen_no, RYBe_, "RYBe")
        self.RYBr = ap.apply_policy(scen_no, RYBr_, "RYBr")
        self.RYBm = ap.apply_policy(scen_no, RYBm_, "RYBm")

        # Scenario
        self.L = sops.IOT.L(self.A)  # L from S and Y modified

        self.yi = np.sum(self.Y, axis=1)  # row sum of final demand
        self.diag_yj = np.diag(self.Y.sum(axis=0))  # column sum of FD
        self.x = sops.IOT.x_IAy(self.L, self.yi)
        self.diag_x = np.diag(self.x)

        self.S = sops.IOT.S(self.A, self.diag_x)

        self.E = sops.IOT.B(self.RE, self.diag_x)  # primary inputs

        self.Be = sops.IOT.B(self.RBe, self.diag_x)  # emissions ext
        self.Br = sops.IOT.B(self.RBr, self.diag_x)  # resource ext
        self.Bm = sops.IOT.B(self.RBm, self.diag_x)  # material ext

        self.YBe = sops.fdext.YB(self.RYBe, self.diag_yj)  # emissions ext
        self.YBr = sops.fdext.YB(self.RYBr, self.diag_yj)  # resource ext
        self.YBm = sops.fdext.YB(self.RYBm, self.diag_yj)  # material ext

        # Characterisation
        self.CrBe = np.matmul(self.SUTs.CrBe, self.Be)  # emissions ext
        self.CrBr = np.matmul(self.SUTs.CrBr, self.Br)  # resource ext
        self.CrBm = np.matmul(self.SUTs.CrBm, self.Bm)  # material ext
        self.CrE = np.matmul(self.SUTs.CrE, self.E)  # factor inputs

        self.CrYBe = np.matmul(self.SUTs.CrBe, self.YBe)  # emissions ext
        self.CrYBr = np.matmul(self.SUTs.CrBr, self.YBr)  # resource ext
        self.CrYBm = np.matmul(self.SUTs.CrBm, self.YBm)  # material ext

        self.ver = sops.verifyIOT(self.S, self.Y, self.E)  # ver_new_IOT
