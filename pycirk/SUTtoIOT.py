# -*- coding:  utf-8 -*-
"""
Created on Mon Feb  6 12: 29: 47 2017

Description:  Uses methods within SUTops to calculate IOT and Extensions

Scope:  Modelling the Circular economy in EEIO

@author:  Franco Donati
@institution:  Leiden University CML
"""
import numpy as np
from pandas import DataFrame as df
from pycirk.labels import relabel
from pycirk.labels import get_labels
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
        self.Be = SUTs["Be"]  # Environmental extension
        self.YBe = SUTs["YBe"]  # Environmental extension final demand
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

        # Collecting labels
        self.prod_get_l_m = get_labels(self.Y, 0)  # with unit column
        self.CrBe_get_l = get_labels(self.CrBe, 0)
        self.CrBr_get_l = get_labels(self.CrBr, 0)
        self.CrBm_get_l = get_labels(self.CrBm, 0)
        self.CrE_get_l = get_labels(self.CrE, 0)

        # without unit column = to be used for extension tables
        self.prod_get_l = get_labels(self.Y, 0, drop_unit=True)

        self.E_get_l = get_labels(self.E, 0)
        self.Y_get_l_m = get_labels(self.Y, 1)
        self.Y_get_l = get_labels(self.Y, 1, drop_unit=True)
        self.Be_get_l = get_labels(self.Be, 0)
        self.Br_get_l = get_labels(self.Br, 0)
        self.Bm_get_l = get_labels(self.Bm, 0)

        del(SUTs)

    def relabel_in_bulk(self, data):
        """
        This function makes sure that everything is labeled in IOT tables
        """

        # Relabel Main IOT elements
        S = relabel(data["S"], self.prod_get_l, self.prod_get_l_m, "S")
        L = relabel(data["L"], self.prod_get_l, self.prod_get_l, "L")
        A = relabel(data["A"], self.prod_get_l_m, self.prod_get_l_m, "A")
        Y = relabel(data["Y"], self.Y_get_l, self.prod_get_l_m, "Y")
        E = relabel(data["E"], self.prod_get_l, self.E_get_l, "E")
        RE = relabel(data["RE"], self.prod_get_l_m, self.E_get_l, "RE")

        # Relabel Inter-trans extensions
        Be = relabel(data["Be"], self.prod_get_l, self.Be_get_l, "Be")
        Br = relabel(data["Br"], self.prod_get_l, self.Br_get_l, "Br")
        Bm = relabel(data["Bm"], self.prod_get_l, self.Bm_get_l, "Bm")

        # Inter-trans extensions' intensities
        RBe = relabel(data["RBe"], self.prod_get_l_m, self.Be_get_l, "RBe")
        RBr = relabel(data["RBr"], self.prod_get_l_m, self.Br_get_l, "RBr")
        RBm = relabel(data["RBm"], self.prod_get_l_m, self.Bm_get_l, "RBm")

        # Relabel characterisation
        CrBe = relabel(data["CrBe"], self.prod_get_l, self.CrBe_get_l, "CrBe")
        CrBr = relabel(data["CrBr"], self.prod_get_l, self.CrBr_get_l, "CrBe")
        CrBm = relabel(data["CrBm"], self.prod_get_l, self.CrBm_get_l, "CrBe")
        CrE = relabel(data["CrE"], self.prod_get_l, self.CrE_get_l, "CrBe")

        # label q
        x = relabel(data["x"], "x", self.prod_get_l_m, "x")
        # label balance verification
        ver_label = "balance (x_out/x_in) - % - 100=balanced - 0=NaN no values"
        ver = relabel(df(data["ver"]), ver_label, self.prod_get_l, "ver")

        # Labeling final demand extensions
        YBe = relabel(data["YBe"], self.Y_get_l, self.Be_get_l, "YBe")

        YBr = relabel(data["YBr"], self.Y_get_l, self.Br_get_l, "YBr")

        YBm = relabel(data["YBm"], self.Y_get_l, self.Bm_get_l, "YBm")

        # Labeling final demand extensions' intensities
        RYBe = relabel(data["RYBe"], self.Y_get_l_m, self.Be_get_l, "RYBe")
        RYBr = relabel(data["RYBr"], self.Y_get_l_m, self.Br_get_l, "RYBr")
        RYBm = relabel(data["RYBm"], self.Y_get_l_m, self.Bm_get_l, "RYBm")

        # Relabel characterisation for final demand
        CrYBe = relabel(data["CrYBe"], self.Y_get_l, self.CrBe_get_l, "CrBe")
        CrYBr = relabel(data["CrYBr"], self.Y_get_l, self.CrBr_get_l, "CrBe")
        CrYBm = relabel(data["CrYBm"], self.Y_get_l, self.CrBm_get_l, "CrBe")

        labelled = {"x": x,
                    "Y": Y,
                    "A": A,
                    "RE": RE,
                    "Be": Be,
                    "RBe": RBe,
                    "Br": Br,
                    "RBr": RBr,
                    "Bm": Bm,
                    "RBm": RBm,
                    "L": L,
                    "E": E,
                    "S": S,
                    "ver": ver,
                    "YBe": YBe,
                    "YBr": YBr,
                    "YBm": YBm,
                    "RYBe": RYBe,
                    "RYBr": RYBr,
                    "RYBm": RYBm,
                    "CrBe": CrBe,
                    "CrBm": CrBm,
                    "CrBr": CrBr,
                    "CrE": CrE,
                    "CrYBe": CrYBe,
                    "CrYBm": CrYBm,
                    "CrYBr": CrYBr
                    }

        return(labelled)

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
        Be = sops.PxP_ITA_TC.B(RBe, self.diag_q)  # environmental extensions

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
               "RBe": RBe,
               "Br": Br,
               "RBr": RBr,
               "Bm": Bm,
               "RBm": RBm,
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
        Be = sops.PxP_ITA_MSC.B(RBe, self.diag_q)  # environmental extensions

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
               "RBe": RBe,
               "Br": Br,
               "RBr": RBr,
               "Bm": Bm,
               "RBm": RBm,
               "L": L,
               "S": S,
               "E": E,
               "x": x,
               "ver": ver_base
               }

        return(IOT)

    @staticmethod
    def IOT(S, Y, E, Be, Br, Bm):
        """
        IOT
        """
        x = sops.IOT.q(S, Y)  # total product output
        diag_x = np.diag(x)
        inv_diag_x = sops.inv(diag_x)

        y = np.sum(Y, axis=1)

        A = sops.IOT.A(S, inv_diag_x)  # technical coefficient matrix
        L = sops.IOT.L(A)  # leontief inverse

        RE = sops.IOT.R(E, inv_diag_x)  # primary inputs coef
        E = sops.IOT.B(RE, diag_x)

        RBe = sops.IOT.R(Be, inv_diag_x)  # Be coefficient matrix
        Be = sops.IOT.B(RBe, diag_x)  # environmental extensions

        RBr = sops.IOT.R(Br, inv_diag_x)  # Br coefficient matrix
        Br = sops.IOT.B(RBr, diag_x)  # resource extensions

        RBm = sops.IOT.R(Bm, inv_diag_x)  # Bm coefficient matrix
        Bm = sops.IOT.B(RBm, diag_x)  # Material extension

        S = sops.IOT.S(A, diag_x)  # intermediates
        x = sops.IOT.x_IAy(L, y)

        ver_base = sops.verifyIOT(S, Y, E)

        IOT = {"A": A,
               "S": S,
               "L": L,
               "S": S,
               "Y": Y,
               "RE": RE,
               "E": E,
               "x": x,
               "Be": Be,
               "RBe": RBe,
               "Br": Br,
               "RBr": RBr,
               "Bm": Bm,
               "RBm": RBm,
               "ver": ver_base
               }

        return(IOT)

    @staticmethod
    def FD_EXT(YB, diag_yj):
        """
        Recalculates FD extensions based on counterfactual final demand
        """
        inv_diag_yj = sops.inv(diag_yj)

        RYB = sops.fdext.RYB(inv_diag_yj, YB)
        YB = sops.fdext.YB(RYB, diag_yj)

        EXT = {
               "RYB": RYB,
               "YB": YB
                }

        return(EXT)
