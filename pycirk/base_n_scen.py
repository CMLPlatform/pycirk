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
from pycirk.utils import dotdict


def organize_data(data):

    E = data["E"]
    RE = data["RE"]
    L = data["L"]
    S = data["S"]
    x = data["x"]
    A = data["A"]
    Y = data["Y"]

    RBe = data["RBe"]
    RBr = data["RBr"]
    RBm = data["RBm"]

    Be = data["Be"]
    Br = data["Br"]
    Bm = data["Bm"]

    CrBe_ = data["CrBe"]
    CrBr_ = data["CrBr"]
    CrBm_ = data["CrBm"]
    CrE_ = data["CrE"]

    ver_base = data["ver"]

    # Calculating intensity matrices for final demand extentions

    YBe_ = data["YBe"]
    YBr_ = data["YBr"]
    YBm_ = data["YBm"]

    diag_yj = np.diag(Y.sum(axis=0))

    _YBe = sops.IOT.FD_EXT(YBe_, diag_yj)
    _YBr = sops.IOT.FD_EXT(YBr_, diag_yj)
    _YBm = sops.IOT.FD_EXT(YBm_, diag_yj)

    YBe = _YBe["YB"]
    YBr = _YBr["YB"]
    YBm = _YBm["YB"]
    RYBe = _YBe["RYB"]
    RYBr = _YBr["RYB"]
    RYBm = _YBm["RYB"]

    # Characterisation
    CrBe = np.matmul(CrBe_, Be)  # emissions ext
    CrBr = np.matmul(CrBr_, Br)  # resource ext
    CrBm = np.matmul(CrBm_, Bm)  # material ext
    CrE = np.matmul(CrE_, E)  # factor inputs

    CrYBe = np.matmul(CrBe_, YBe)  # emissions ext
    CrYBr = np.matmul(CrBr_, YBr)  # resource ext
    CrYBm = np.matmul(CrBm_, YBm)  # material ext

    IOT = {"RE": RE,
           "A": A,
           "Y": Y,
           "Be": Be,
           "RBe": RBe,
           "YBe": YBe,
           "RYBe": RYBe,
           "Br": Br,
           "RBr": RBr,
           "YBr": YBr,
           "RYBr": RYBr,
           "Bm": Bm,
           "RBm": RBm,
           "YBm": YBm,
           "RYBm": RYBm,
           "CrBe": CrBe,
           "CrBm": CrBm,
           "CrBr": CrBr,
           "CrYBe": CrYBe,
           "CrYBm": CrYBm,
           "CrYBr": CrYBr,
           "CrE": CrE,
           "L": L,
           "S": S,
           "E": E,
           "x": x,
           "ver": ver_base
           }

    return(dotdict(IOT))


def sceneIOT(data, scen_no, scen_file):
    """
    baseline IOT calculated with Technical Coefficient or
    Market coefficient method
    """

    ap = Apply_policy(scen_file)

    Y_ = data.Y.copy(True)
    S_ = data.S.copy(True)
    RE_ = data.RE.copy(True)
    RBe_ = data.RBe.copy(True)
    RBr_ = data.RBr.copy(True)
    RBm_ = data.RBm.copy(True)
    RYBe_ = data.RYBe.copy(True)
    RYBr_ = data.RYBr.copy(True)
    RYBm_ = data.RYBm.copy(True)

    # Apply policy to economic matrices
    S_ = ap.apply_policy(scen_no, S_, "S")
    inv_diag_x = sops.inv(np.diag(sops.IOT.x(S_, Y_)))
    A_ = sops.IOT.A(S_, inv_diag_x)
    data.A = ap.apply_policy(scen_no, df(A_), "A")

    Y = ap.apply_policy(scen_no, Y_, "Y")
    RE = ap.apply_policy(scen_no, RE_, "RE")

    # Apply policy to intermediate extension coefficient matrices
    data.RBe = ap.apply_policy(scen_no, RBe_, "RBe")
    data.RBr = ap.apply_policy(scen_no, RBr_, "RBr")
    data.RBm = ap.apply_policy(scen_no, RBm_, "RBm")

    # Apply policy to  final demand extension coefficient matrices
    data.RYBe = ap.apply_policy(scen_no, RYBe_, "RYBe")
    data.RYBr = ap.apply_policy(scen_no, RYBr_, "RYBr")
    data.RYBm = ap.apply_policy(scen_no, RYBm_, "RYBm")

    # Scenario
    data.L = sops.IOT.L(A_)  # L from S and Y modified

    yi = np.sum(Y, axis=1)  # row sum of final demand
    diag_yj = np.diag(Y.sum(axis=0))  # column sum of FD
    x = sops.IOT.x_IAy(L, yi)
    diag_x = np.diag(x)

    S = sops.IOT.S(A, diag_x)

    E = sops.IOT.B(RE, diag_x)  # primary inputs

    Be = sops.IOT.B(RBe, diag_x)  # emissions ext
    Br = sops.IOT.B(RBr, diag_x)  # resource ext
    Bm = sops.IOT.B(RBm, diag_x)  # material ext

    YBe = sops.IOT.FD_EXT(RYBe, diag_yj)  # emissions ext
    YBr = sops.IOT.FD_EXT(RYBr, diag_yj)  # resource ext
    YBm = sops.IOT.FD_EXT(RYBm, diag_yj)  # material ext

    # Characterisation
    CrBe = np.matmul(CrBe_, Be)  # emissions ext
    CrBr = np.matmul(CrBr_, Br)  # resource ext
    CrBm = np.matmul(CrBm_, Bm)  # material ext
    CrE = np.matmul(CrE_, E)  # factor inputs

    CrYBe = np.matmul(CrBe_, YBe)  # emissions ext
    CrYBr = np.matmul(CrBr_, YBr)  # resource ext
    CrYBm = np.matmul(CrBm_, YBm)  # material ext

    ver = sops.verifyIOT(S, Y, E)  # ver_new_IOT
