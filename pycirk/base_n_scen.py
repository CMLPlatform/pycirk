# -*- coding: utf-8 -*-
"""
Created on Tue Feb 7 16:29:23 2017

Description: Calculate baseline and scenarios in IOT

Scope: Modelling the Circular economy in EEIO


@author: Franco Donati
@institution: Leiden University CML
"""

import warnings
import numpy as np
from pandas import DataFrame as df
import pycirk.SUTtoIOT as SUTtoIOT
from pycirk.SUTops import SUTops as sops
from pycirk.labels import get_labels
from pycirk.labels import relabel
from pycirk.apply_policy import Apply_policy


class Base_n_scen:
    """
    Loads base data and assembles new tables (scenario) from the processed data
    """
    def __init__(self, data, method):
        """
        Define the settings for the base data
        method = 0 (IOTpxpSTA_TCm)
        method = 1 (IOTpxpSTA_MSCm)
        """

        self.SUTs = SUTtoIOT.Transform(data)

        self.FD_EXT = SUTtoIOT.Transform.FD_EXT
# =============================================================================
#         Transform SUT to IOT and outputting elements necessary for operations
# =============================================================================
        if int(method) == 0:
            self.IOT = self.SUTs.IOTpxpSTA_TCm()
        elif int(method) == 1:
            self.IOT = self.SUTs.IOTpxpSTA_MSCm()

    def baseIOT(self):
        """
        method = 0 (Technical coefficient method)
        method = 1 (market share coefficient method)

        baseline IOT and relabelling
        """
        # Loading elements

        E = self.IOT["E"]
        RE = self.IOT["RE"]
        L = self.IOT["L"]
        S = self.IOT["S"]
        x = self.IOT["x"]
        A = self.IOT["A"]
        Y = self.IOT["Y"]
#        print("l_m", df(Y.index).iloc[0])

        RBe = self.IOT["RBe"]
        RBr = self.IOT["RBr"]
        RBm = self.IOT["RBm"]

        Be = self.IOT["Be"]
        Br = self.IOT["Br"]
        Bm = self.IOT["Bm"]
        ver_base = self.IOT["ver"]

        # Calculating intensity matrices for final demand extentions

        YBe_ = self.FD_EXT(self.SUTs.YBe, self.SUTs.diag_yj)
        YBr_ = self.FD_EXT(self.SUTs.YBr, self.SUTs.diag_yj)
        YBm_ = self.FD_EXT(self.SUTs.YBm, self.SUTs.diag_yj)

        YBe = YBe_["YB"]
        YBr = YBr_["YB"]
        YBm = YBm_["YB"]
        RYBe = YBe_["RYB"]
        RYBr = YBr_["RYB"]
        RYBm = YBm_["RYB"]

        # Characterisation
        CrBe = np.matmul(self.SUTs.CrBe, Be)  # environmental ext
        CrBr = np.matmul(self.SUTs.CrBr, Br)  # resource ext
        CrBm = np.matmul(self.SUTs.CrBm, Bm)  # material ext
        CrE = np.matmul(self.SUTs.CrE, E)  # factor inputs

        CrYBe = np.matmul(self.SUTs.CrBe, YBe)  # environmental ext
        CrYBr = np.matmul(self.SUTs.CrBr, YBr)  # resource ext
        CrYBm = np.matmul(self.SUTs.CrBm, YBm)  # material ext

        IOT = {"Y": Y,
               "L": L,
               "A": A,
               "S": S,
               "x": x,
               "RE": RE,
               "E": E,
               "YBe": YBe,
               "YBr": YBr,
               "YBm": YBm,
               "RYBe": RYBe,
               "RYBr": RYBr,
               "RYBm": RYBm,
               "RBe": RBe,
               "RBr": RBr,
               "RBm": RBm,
               "Be": Be,
               "Br": Br,
               "Bm": Bm,
               "ver": ver_base,
               "CrBe": CrBe,
               "CrYBe": CrYBe,
               "CrBr": CrBr,
               "CrYBr": CrYBr,
               "CrBm": CrBm,
               "CrYBm": CrYBm,
               "CrE": CrE
               }

        IOT_lb = self.SUTs.relabel_in_bulk(IOT)
        del(IOT)

        return(IOT_lb)

    def sceneIOT(self, scen_no, scen_file, base=None):
        """
        baseline IOT calculated with Technical Coefficient or
        Market coefficient method
        """

        if scen_no in [0, "baseline", "base"]:
            warnings.warn("You specified the baseline so no changes were made."
                          "Baseline was returned. Possible scenarios [1,2,n]")
            return(self.baseIOT())

        if base is None:
            base = self.baseIOT()

        ap = Apply_policy(scen_file)

        # A_ = base["A"].copy(True)
        Y_ = base["Y"].copy(True)
        S_ = base["S"].copy(True)
        RE_ = base["RE"].copy(True)
        RBe_ = base["RBe"].copy(True)
        RBr_ = base["RBr"].copy(True)
        RBm_ = base["RBm"].copy(True)
        RYBe_ = base["RYBe"].copy(True)
        RYBr_ = base["RYBr"].copy(True)
        RYBm_ = base["RYBm"].copy(True)
        del(base)

        prod_get_l_m = get_labels(S_, 0)  # get the label

        # Apply policy to economic matrices

        S_ = ap.apply_policy(scen_no, S_, "S")
        inv_diag_x = sops.inv(np.diag(sops.IOT.x(S_, Y_)))
        A_ = sops.IOT.A(S_, inv_diag_x)
        A_ = relabel(A_, prod_get_l_m, prod_get_l_m, "A")
        A = ap.apply_policy(scen_no, df(A_), "A")

        Y = ap.apply_policy(scen_no, Y_, "Y")
        RE = ap.apply_policy(scen_no, RE_, "RE")

        # Apply policy to intermediate extension coefficient matrices
        RBe = ap.apply_policy(scen_no, RBe_, "RBe")
        RBr = ap.apply_policy(scen_no, RBr_, "RBr")
        RBm = ap.apply_policy(scen_no, RBm_, "RBm")

        # Apply policy to  final demand extension coefficient matrices
        RYBe = ap.apply_policy(scen_no, RYBe_, "RYBe")
        RYBr = ap.apply_policy(scen_no, RYBr_, "RYBr")
        RYBm = ap.apply_policy(scen_no, RYBm_, "RYBm")

        # Scenario
        L = sops.IOT.L(A)  # Leontief inv from scenario with S and Y modified

        yi = np.sum(Y, axis=1)  # row sum of final demand
        diag_yj = np.diag(Y.sum(axis=0))  # column sum of final demand
        x = sops.IOT.x_IAy(L, yi)
        diag_x = np.diag(x)

        S = sops.IOT.S(A, diag_x)

        E = sops.IOT.B(RE, diag_x)  # primary inputs

        Be = sops.IOT.B(RBe, diag_x)  # environmental ext
        Br = sops.IOT.B(RBr, diag_x)  # resource ext
        Bm = sops.IOT.B(RBm, diag_x)  # material ext

        YBe = sops.fdext.YB(RYBe, diag_yj)  # environmental ext
        YBr = sops.fdext.YB(RYBr, diag_yj)  # resource ext
        YBm = sops.fdext.YB(RYBm, diag_yj)  # material ext

        # Characterisation
        CrBe = np.matmul(self.SUTs.CrBe, Be)  # environmental ext
        CrBr = np.matmul(self.SUTs.CrBr, Br)  # resource ext
        CrBm = np.matmul(self.SUTs.CrBm, Bm)  # material ext
        CrE = np.matmul(self.SUTs.CrE, E)  # factor inputs

        CrYBe = np.matmul(self.SUTs.CrBe, YBe)  # environmental ext
        CrYBr = np.matmul(self.SUTs.CrBr, YBr)  # resource ext
        CrYBm = np.matmul(self.SUTs.CrBm, YBm)  # material ext

        ver = sops.verifyIOT(S, Y, E)  # ver_new_IOT

        IOT = {"Y": Y,
               "L": L,
               "A": A,
               "S": S,
               "x": x,
               "RE": RE,
               "E": E,
               "YBe": YBe,
               "YBr": YBr,
               "YBm": YBm,
               "RYBe": RYBe,
               "RYBr": RYBr,
               "RYBm": RYBm,
               "RBe": RBe,
               "RBr": RBr,
               "RBm": RBm,
               "Be": Be,
               "Br": Br,
               "Bm": Bm,
               "ver": ver,
               "CrBe": CrBe,
               "CrYBe": CrYBe,
               "CrBr": CrBr,
               "CrYBr": CrYBr,
               "CrBm": CrBm,
               "CrYBm": CrYBm,
               "CrE": CrE
               }

        IOT_lb = self.SUTs.relabel_in_bulk(IOT)

        return(IOT_lb)
