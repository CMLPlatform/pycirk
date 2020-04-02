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

        w = met.B(self.W, T, self.inv_diag_q)  # primary inp. coef matrix

        Z = met.Z(T, self.U)  # intermediates
        x = ops.IOT.x_IAy(L, self.yi)
        W = ops.IOT.R(w, np.diag(x))
        ver_base = ops.verifyIOT(Z, self.Y, W)
        del(self.V)
        del(self.U)
        del(self.W)

        e = met.B(self.E, T, self.inv_diag_q)  # emis coef. matrix
        del(self.E)
        E = met.R(e, np.diag(x))

        r = met.B(self.R, T, self.inv_diag_q)  # resour coef. matrix
        del(self.R)
        R = met.R(r, np.diag(x))

        m = met.B(self.M, T, self.inv_diag_q)  # mater coef. matrix
        del(self.M)
        M = met.R(m, np.diag(x))

        A = ops.IOT.A(Z, self.inv_diag_q)

        return {"Y": self.Y,
                "L": L,
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

        S = met.S(self.U, self.inv_diag_g)  # ind. interm. coef. => in EUROSTAT manual shown as S
        D = met.D(self.V, self.inv_diag_q)  # Market shares
        A = met.A(S, D)  # technical coefficient matrix
        
        L = met.L(A)  # leontief inverse
        w = met.B(self.W, D, self.inv_diag_g)  # primary inputs
        x = ops.IOT.x_IAy(L, self.yi)
        W = ops.IOT.R(w, np.diag(x))
        Z = met.Z(S, D, np.diag(x))  # intermediates
        ver_base = ops.verifyIOT(Z, self.Y, W)
        del(self.V)
        del(self.U)
        del(self.W)

        e = met.B(self.E, D, self.inv_diag_g)  # emis coef. matrix
        del(self.E)
        E = met.R(e, np.diag(x))

        r = met.B(self.R, D, self.inv_diag_g)  # resour coef. matrix
        del(self.R)
        R = met.R(r, np.diag(x))

        m = met.B(self.M, D, self.inv_diag_g)  # mater coef. matrix
        del(self.M)
        M = met.R(m, np.diag(x))

        return {"Y": self.Y,
                "L": L,
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
