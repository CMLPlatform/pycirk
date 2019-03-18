# -*- coding:  utf-8 -*-
"""
Created on Mon Feb  6 12: 29: 47 2017

Description:  Uses methods within SUTops to calculate IOT and Extensions

Scope:  Modelling the Circular economy in EEIO

@author:  Franco Donati
@institution:  Leiden University CML
"""
import numpy as np
from pycirk.SUTops import SUTops as sops


class Transform:
    """
    Transforms SUTs to IOT an calcualate extensions
    """

    def __init__(self, SUTs):

        # Baseline monetary data
        self.V = SUTs["V"]  # Supply matrix
        self.U = SUTs["U"]  # Intermediate use
        self.Y = SUTs["Y"]  # Final demand
#        self.Tm = SUTs["Tm"] # Trade margins
        self.E = SUTs["E"]  # Primary input
        self.Be = SUTs["Be"]  # emissions extension
        self.YBe = SUTs["YBe"]  # emissions extension final demand
        self.Br = SUTs["Br"]  # Resources extension
        self.YBr = SUTs["YBr"]  # Resources extension final demand
        self.Bm = SUTs["Bm"]  # Materials extension
        self.YBm = SUTs["YBm"]  # Materials extension final demand

        self.CrBe = SUTs["CrBe"]  # Characterisation emissions
        self.CrBm = SUTs["CrBm"]  # Characterisation materials
        self.CrBr = SUTs["CrBr"]  # Characterisation resources
        self.CrE = SUTs["CrE"]  # Characterisation factor inputs

        # baseline variables
        self.e = np.sum(self.E[: 9], axis=0)
        self.yi = np.array(np.sum(self.Y, axis=1))  # row sum of final demand
        self.yj = np.array(np.sum(self.Y, axis=0))  # col sum of final demand
        self.q = np.sum(self.V, axis=1)  # total product output
        self.g = np.sum(self.V, axis=0)  # total industry output

        # bv diagonals
        self.diag_q = np.diag(self.q)  # diagonal of q
        self.diag_g = np.diag(self.g)  # diagonal of g
        self.diag_yi = np.diag(self.yi)  # diagonal of yi
        self.diag_yj = np.diag(self.yj)  # diagonal of yj

        # bv inverses
        self.inv_diag_yi = sops.inv(self.diag_yi)
        self.inv_diag_yj = sops.inv(self.diag_yj)
        self.inv_diag_q = sops.inv(self.diag_q)
        self.inv_diag_g = sops.inv(self.diag_g)

        del(SUTs)

    def IOTpxpSTA_TCm(self):
        """
        IOT prod x prod Single tech Industry-technology assumption
        Technical coef method
        """
        T = sops.PxP_ITA_TC.T(self.V, self.inv_diag_g)  # transformation matrix
        L = sops.PxP_ITA_TC.L(self.U, T, self.inv_diag_q)  # leontief inverse
        RE = sops.PxP_ITA_TC.R(self.E, T, self.inv_diag_q)  # primary inp. coef
        E = sops.PxP_ITA_TC.B(RE, self.diag_q)  # primary inputs

        RBe = sops.PxP_ITA_TC.R(self.Be, T, self.inv_diag_q)  # Be coef. matrix
        Be = sops.PxP_ITA_TC.B(RBe, self.diag_q)  # emissions extensions

        RBr = sops.PxP_ITA_TC.R(self.Br, T, self.inv_diag_q)  # Br coef. matrix
        Br = sops.PxP_ITA_TC.B(RBr, self.diag_q)  # resource extensions

        RBm = sops.PxP_ITA_TC.R(self.Bm, T, self.inv_diag_q)  # Bm coef. matrix
        Bm = sops.PxP_ITA_TC.B(RBm, self.diag_q)  # Material extension

        S = sops.PxP_ITA_TC.S(T, self.U)  # intermediates
        x = sops.IOT.x_IAy(L, self.yi)  # total product ouput

        A = sops.IOT.A(S, self.inv_diag_q)

        Y = self.Y

        ver_base = sops.verifyIOT(S, Y, E)

        IOT = {"x": x,
               "T": T,
               "Y": Y,
               "A": A,
               "RE": RE,
               "Be": Be,
               "YBe": self.YBe,
               "RBe": RBe,
               "Br": Br,
               "YBr": self.YBr,
               "RBr": RBr,
               "Bm": Bm,
               "YBm": self.YBm,
               "RBm": RBm,
               "CrBe": self.CrBe,
               "CrBm": self.CrBm,
               "CrBr": self.CrBr,
               "CrE": self.CrE,
               "L": L,
               "E": E,
               "S": S,
               "ver": ver_base
               }

        return(IOT)

    def IOTpxpSTA_MSCm(self):
        """
        IOT prod x prod Single tech Industry-technology assumption
        Market share coef method
        """
        Z = sops.PxP_ITA_MSC.Z(self.U, self.inv_diag_g)  # ind. interm. coef.
        D = sops.PxP_ITA_MSC.D(self.V, self.inv_diag_q)  # Market shares
        A = sops.PxP_ITA_MSC.A(Z, D)  # technical coefficient matrix
        L = sops.PxP_ITA_MSC.L(A)  # leontief inverse
        RE = sops.PxP_ITA_MSC.R(self.E, D, self.inv_diag_g)  # primary inputs
        E = sops.PxP_ITA_MSC.B(RE, self.diag_q)

        RBe = sops.PxP_ITA_MSC.R(self.Be, D, self.inv_diag_g)  # Be coef. matr.
        Be = sops.PxP_ITA_MSC.B(RBe, self.diag_q)  # emissions extensions

        RBr = sops.PxP_ITA_MSC.R(self.Br, D, self.inv_diag_g)  # Br coef. matr.
        Br = sops.PxP_ITA_MSC.B(RBr, self.diag_q)  # resource extensions

        RBm = sops.PxP_ITA_MSC.R(self.Bm, D, self.inv_diag_g)  # Bm coef. matr.
        Bm = sops.PxP_ITA_MSC.B(RBm, self.diag_q)  # Material extension

        S = sops.PxP_ITA_MSC.S(Z, D, self.diag_q)  # intermediates
        x = sops.IOT.x_IAy(L, self.yi)  # total product output

        A = sops.IOT.A(S, self.inv_diag_q)

        Y = self.Y

        ver_base = sops.verifyIOT(S, Y, E)

        IOT = {"RE": RE,
               "A": A,
               "Y": Y,
               "D": D,
               "Be": Be,
               "YBe": self.YBe,
               "RBe": RBe,
               "Br": Br,
               "YBr": self.YBr,
               "RBr": RBr,
               "Bm": Bm,
               "YBm": self.YBm,
               "RBm": RBm,
               "CrBe": self.CrBe,
               "CrBm": self.CrBm,
               "CrBr": self.CrBr,
               "CrE": self.CrE,
               "L": L,
               "S": S,
               "E": E,
               "x": x,
               "ver": ver_base
               }

        return(IOT)
