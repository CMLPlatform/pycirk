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
        self.V = np.array(SUTs["V"])  # Supply matrix
        self.U = np.array(SUTs["U"])  # Intermediate use
        self.Y = np.array(SUTs["Y"])  # Final demand
        self.W = np.array(SUTs["W"])  # Primary input
        self.E = np.array(SUTs["E"])  # emissions extension
        self.EY = np.array(SUTs["YE"])  # emissions extension final demand
        self.R = np.array(SUTs["R"])  # Resources extension
        self.RY = np.array(SUTs["YR"])  # Resources extension final demand
        self.M = np.array(SUTs["M"])  # Materials extension
        self.MY = np.array(SUTs["YM"])  # Materials extension final demand

        self.Cr_E_k = SUTs["Cr_E_k"]  # Charact coefficients emissions
        self.Cr_R_k = SUTs["Cr_R_k"]  # Charact coefficients resources
        self.Cr_M_k = SUTs["Cr_M_k"]  # Charact coefficients materials
        self.Cr_W_k = SUTs["Cr_W_k"]  # Charact coefficients factor inputs

        # baseline variables
        self.yi = np.array(np.sum(self.Y, axis=1))  # row sum of final demand
        self.yj = np.array(np.sum(self.Y, axis=0))  # col sum of final demand
        self.q = np.sum(self.V, axis=1)  # total product output
        self.g = np.sum(self.V, axis=0)  # total industry output

        # bv inverses, kept as vectors: multiplying by a diagonal matrix is
        # an element-wise scaling, so the n x n diagonals are never built
        self.inv_q = ops.inv(self.q)
        self.inv_g = ops.inv(self.g)

        del(SUTs)

    def IOTpxpSTA_TCm(self):
        """
        IOT prod x prod Single tech Industry-technology assumption
        Technical coef method
        """
        met = ops.PxP_ITA_TC

        T = met.T(self.V, self.inv_g)  # transformation matrix

        w = met.B(self.W, T, self.inv_q)  # primary inp. coef matrix

        Z = met.Z(T, self.U)  # intermediates
        A = ops.IOT.A(Z, self.inv_q)
        x = ops.IOT.x_solve(np.nan_to_num(A, copy=False), self.yi)
        W = ops.IOT.R(w, x)
        ver_base = ops.verifyIOT(Z, self.Y, W)
        del(self.V)
        del(self.U)
        del(self.W)

        e = met.B(self.E, T, self.inv_q)  # emis coef. matrix
        del(self.E)
        E = met.R(e, x)

        r = met.B(self.R, T, self.inv_q)  # resour coef. matrix
        del(self.R)
        R = met.R(r, x)

        m = met.B(self.M, T, self.inv_q)  # mater coef. matrix
        del(self.M)
        M = met.R(m, x)

        return {"Y": self.Y,
                "Z": Z,
                "A": A,
                "W": W,
                "E": E,
                "EY": self.EY,
                "R": R,
                "RY": self.RY,
                "M": M,
                "MY": self.MY,
                "Cr_E_k": self.Cr_E_k,
                "Cr_M_k": self.Cr_M_k,
                "Cr_R_k": self.Cr_R_k,
                "Cr_W_k": self.Cr_W_k,
                "ver_base": ver_base
                }

    def IOTpxpSTA_MSCm(self):
        """
        IOT prod x prod Single tech Industry-technology assumption
        Market share coef method
        """
        met = ops.PxP_ITA_MSC

        S = met.S(self.U, self.inv_g)  # ind. interm. coef. => in EUROSTAT manual shown as S
        D = met.D(self.V, self.inv_q)  # Market shares
        A = met.A(S, D)  # technical coefficient matrix

        w = met.B(self.W, D, self.inv_g)  # primary inputs
        x = ops.IOT.x_solve(A, self.yi)
        W = ops.IOT.R(w, x)
        Z = ops.IOT.Z(A, x)  # intermediates
        ver_base = ops.verifyIOT(Z, self.Y, W)
        del(self.V)
        del(self.U)
        del(self.W)

        e = met.B(self.E, D, self.inv_g)  # emis coef. matrix
        del(self.E)
        E = met.R(e, x)

        r = met.B(self.R, D, self.inv_g)  # resour coef. matrix
        del(self.R)
        R = met.R(r, x)

        m = met.B(self.M, D, self.inv_g)  # mater coef. matrix
        del(self.M)
        M = met.R(m, x)

        return {"Y": self.Y,
                "Z": Z,
                "A": A,
                "W": W,
                "E": E,
                "EY": self.EY,
                "R": R,
                "RY": self.RY,
                "M": M,
                "MY": self.MY,
                "Cr_E_k": self.Cr_E_k,
                "Cr_M_k": self.Cr_M_k,
                "Cr_R_k": self.Cr_R_k,
                "Cr_W_k": self.Cr_W_k,
                "ver_base": ver_base
                }

        # Add here more transformation methods for industry-by-industry
