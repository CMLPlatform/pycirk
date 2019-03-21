# -*- coding:  utf-8 -*-
"""
Created on Mon Feb  6 12: 29: 47 2017

Description:  Uses methods within SUTops to calculate IOT and Extensions

Scope:  Modelling the Circular economy in EEIO

@author:  Franco Donati
@institution:  Leiden University CML
"""
import numpy as np
from pycirk.fundamental_operations import Operations as ops

class Transform:
    """
    Transforms SUTs to IOT an calcualate extensions
    """

    def __init__(self, SUTs):

        # Baseline monetary data
        self.V = SUTs["V"]  # Supply matrix
        self.U = SUTs["U"]  # Intermediate use
        self.Y = SUTs["Y"]  # Final demand
        self.E = SUTs["E"]  # Primary input
        self.Be = SUTs["Be"]  # emissions extension
        self.YBe = SUTs["YBe"]  # emissions extension final demand
        self.Br = SUTs["Br"]  # Resources extension
        self.YBr = SUTs["YBr"]  # Resources extension final demand
        self.Bm = SUTs["Bm"]  # Materials extension
        self.YBm = SUTs["YBm"]  # Materials extension final demand

        self.CrBe_k = SUTs["CrBe"]  # Characterisation coefficients emissions
        self.CrBm_k = SUTs["CrBm"]  # Characterisation coefficients materials
        self.CrBr_k = SUTs["CrBr"]  # Characterisation coefficients resources
        self.CrE_k = SUTs["CrE"]  # Characterisation coefficients factor inputs

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
        self.inv_diag_yi = ops.inv(self.diag_yi)
        self.inv_diag_yj = ops.inv(self.diag_yj)
        self.inv_diag_q = ops.inv(self.diag_q)
        self.inv_diag_g = ops.inv(self.diag_g)

        del(SUTs)

    def IOTpxpSTA_TCm(self):
        """
        IOT prod x prod Single tech Industry-technology assumption
        Technical coef method
        """
        met = ops.PxP_ITA_TC
        
        T = met.T(self.V, self.inv_diag_g)  # transformation matrix
        L = met.L(self.U, T, self.inv_diag_q)  # leontief inverse
        RE = met.R(self.E, T, self.inv_diag_q)  # primary inp. coef
        E = met.B(RE, self.diag_q)  # primary inputs

        RBe = met.R(self.Be, T, self.inv_diag_q)  # Be coef. matrix
        Be = met.B(RBe, self.diag_q)  # emissions extensions

        RBr = met.R(self.Br, T, self.inv_diag_q)  # Br coef. matrix
        Br = met.B(RBr, self.diag_q)  # resource extensions

        RBm = met.R(self.Bm, T, self.inv_diag_q)  # Bm coef. matrix
        Bm = met.B(RBm, self.diag_q)  # Material extension

        S = met.S(T, self.U)  # intermediates
        x = ops.IOT.x_IAy(L, self.yi)  # total product ouput

        A = ops.IOT.A(S, self.inv_diag_q)

        Y = self.Y

        ver_base = ops.verifyIOT(S, Y, E)

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
               "CrBe_k": self.CrBe_k,
               "CrBm_k": self.CrBm_k,
               "CrBr_k": self.CrBr_k,
               "CrE_k": self.CrE_k,
               "L": L,
               "E": E,
               "S": S,
               "ver_base": ver_base
               }

        return(IOT)

    def IOTpxpSTA_MSCm(self):
        """
        IOT prod x prod Single tech Industry-technology assumption
        Market share coef method
        """
        met = ops.PxP_ITA_MSC
        
        Z = met.Z(self.U, self.inv_diag_g)  # ind. interm. coef.
        D = met.D(self.V, self.inv_diag_q)  # Market shares
        A = met.A(Z, D)  # technical coefficient matrix
        L = met.L(A)  # leontief inverse
        RE = met.R(self.E, D, self.inv_diag_g)  # primary inputs
        E = met.B(RE, self.diag_q)

        RBe = met.R(self.Be, D, self.inv_diag_g)  # Be coef. matr.
        Be = met.B(RBe, self.diag_q)  # emissions extensions

        RBr = met.R(self.Br, D, self.inv_diag_g)  # Br coef. matr.
        Br = met.B(RBr, self.diag_q)  # resource extensions

        RBm = met.R(self.Bm, D, self.inv_diag_g)  # Bm coef. matr.
        Bm = met.B(RBm, self.diag_q)  # Material extension

        S = met.S(Z, D, self.diag_q)  # intermediates
        x = ops.IOT.x_IAy(L, self.yi)  # total product output

        A = ops.IOT.A(S, self.inv_diag_q)

        Y = self.Y

        ver_base = ops.verifyIOT(S, Y, E)

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
               "CrBe_k": self.CrBe_k,
               "CrBm_k": self.CrBm_k,
               "CrBr_k": self.CrBr_k,
               "CrE_k": self.CrE_k,
               "L": L,
               "S": S,
               "E": E,
               "x": x,
               "ver_base": ver_base
               }

        return(IOT)
