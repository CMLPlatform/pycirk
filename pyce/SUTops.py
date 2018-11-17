# -*- coding: utf-8 -*-
"""
Created on Wed Nov  2 12:05:08 2016

Description: Class to perform SUT and IOT transformations and balancing

Scope: Modelling circular economy policies in EEIOA

@author:Franco Donati
@institution:Leiden University CML
"""
import numpy as np
from numpy import linalg as ln


class SUTops:
    """
    Contains all basic operations to transform SUTs into IOTs and verify them
    It contains two subclasses defining two different trasformation methods
    PxP ITA Market share and Technical Coefficient methods
    note: It should be expanded to other transformation methods in the future
    """
    def inv(x):
        """
        Returns inverse by dividing by 1 and eliminating inf and nan values
        """
        with np.errstate(divide="ignore", invalid="ignore"):
            x = 1/x
        x[x == np.inf] = 0
        x[x == np.nan] = 0

        return(x)

    def var(self, V, U, Y, E):
        """
        Returns variables that are useful in all calculations
        """
        V = np.mat(V)
        U = np.mat(U)
        Y = np.mat(Y)
        E = np.mat(E)

        e = E[:9].sum(axis=0).getA1()
        yi = Y.sum(axis=1).getA1()
        yj = Y.sum(axis=0).getA1()
        q = V.sum(axis=1).getA1()
        g = V.sum(axis=0).getA1()

        diag_yi = np.diag(yi)
        inv_diag_yi = self.inv(diag_yi)

        diag_yj = np.diag(yj)
        inv_diag_yj = self.inv(diag_yj)

        diag_q = np.diag(q)
        inv_diag_q = self.inv(diag_q)

        diag_g = np.diag(g)
        inv_diag_g = self.inv(diag_g)

        p = {"e": e,
             "yi": yi,
             "yj": yj,
             "q": q,
             "g": g,
             "diag_q": diag_q,
             "diag_g": diag_g,
             "diag_yi": diag_yi,
             "diag_yj": diag_yj,
             "inv_diag_q": inv_diag_q,
             "inv_diag_g": inv_diag_g,
             "inv_diag_yi": inv_diag_yi,
             "inv_diag_yj": inv_diag_yj
             }

        return(p)

    class PxP_ITA_TC:
        """
        Model with Transformation Coefficients
        ProdxProd Industry Technology assumption
        """

        def T(V, inv_diag_g):
            """
            Transformation matrix
            T = inv(diag(g)) * V
            """
            # V.transpose because it's in MAKE table instead of SUPPLY
            T = inv_diag_g @ V.transpose()

            return (T)

        def L(U, T, inv_diag_q):
            """
            Input coefficients intermediates
            A = U * T * inv[diag (q)]

            Multiplier matrix
            L =  (I-A)^-1
            """
            A = U @ T @ inv_diag_q  # technical coefficient matrix
            IA = np.identity(len(A)) - A
            L = ln.inv(IA)

            return(L)

        def R(B, T, inv_diag_q):
            """
            Value added and extension requirement matrix
            R = E * inv(diag(g))
            """
            BT = B @ T
            R = BT @ inv_diag_q  # Input coefficients
            return (R)

        def B(R, diag_q):
            """
            Extensions and primary input for IO tables
            """
            B = R @ diag_q

            return (B)

        def S(T, U):
            """
            Intemediates
            S = U * T
            """
            S = U @ T

            return(S)

    class PxP_ITA_MSC:
        """
        Model with Market Share Coef.
        Prod x Prod Industry Technology assumption
        """
        # new update of numpy broke consistency of @ operator
        # where the exceptional behaviour appeared I substituted
        # @ with np.matmul(), this is to be changed in the future

        def Z(U, inv_diag_g):
            """
            Input requirements
            Z = U * inv(diag(g))
            """
            Z = U @ inv_diag_g

            return(Z)

        def D(V, inv_diag_q):
            """
            Market share coefficients
            D = V * inv(diag(q))
            """
            # V.transpose because it's in MAKE table instead of SUPPLY
            D = V.transpose() @ inv_diag_q

            return(D)

        def A(Z, D):
            """
            Total requirement multipliers
            A = Z * D
            """
            A = np.matmul(Z, D)
            return(A)

        def L(A):
            """
            Leontief inverse
            L = (I-A)^-1
            """
            IA = np.identity(len(A)) - A
            L = ln.inv(IA)

            return(L)

        def R(B, D, inv_diag_g):
            """
            Input coefficients ext_matrix
            R = E * inv(diag(g))
            """
            R_ = B @ inv_diag_g
            R = np.matmul(R_, D)
            return (R)

        def B(R, diag_q):
            """
            Extensions and primary input for IO tables
            """
            B = R @ diag_q

            return (B)

        def S(Z, D, diag_q):
            """
            Intermediates
            S = Z * D * diag(q)
            """
            S = np.matmul(Z, D) @ diag_q

            return (S)

    class IOT:
        """
        General IOT operations subclass
        some methods repeat from other subclasses
        but it's good to have them divided for clarity
        """

        def x(S, Y):
            """
            total product output s the sum of Si and y
            """
            q = np.sum(np.array(S), axis=1) + np.sum(np.array(Y), axis=1)

            return(q)

        def R(B, inv_diag_x):
            """
            Primary input and intermediates extensions coefficient matrix
            """
            R = B @ inv_diag_x

            return(R)

        def B(R, diag_x):
            """
            Primary input and intermediates extensions matrix
            """
            B = R @ diag_x

            return(B)

        def x_IAy(L, y):
            """
            Total product ouput
            x = inv(I - A) * yi
            """
            x = np.dot(L, y)

            return (x)

        def S(A, diag_x):
            """
            Total product ouput
            S = A * diag_x
            """
            S = A @ diag_x

            return(S)

        def A(S, inv_diag_x):
            """
            Technical coefficient matrix
            A = S * inv(diag(x))
            """
            A = S @ inv_diag_x

            return(A)

        def L(A):
            """
            Leontief inverse
            L = (I-A)^-1
            """
            IA = np.identity(len(A)) - A
            L = ln.inv(IA)

            return(L)

    class fdext:

        def RYB(inv_diag_yj, YB):
            """
            Method for transformation matrix of YB
            (e.g. final demand emissions)
            RB = YB * inv(diag(yj))
            """
            YRB = YB @ inv_diag_yj

            return (YRB)

        def YB(YRB, diag_yj):
            """
            Extensions and primary input for IO tables
            """
            YB = YRB @ diag_yj

            return (YB)

    class difference:
        """
        This class is used to calculate the difference between scenarios
        """

        def delta_Y(Y, Yalt):
            """
            method to calculate difference in Y
            Y = final demand baseline
            Yalt = final demand scenario
            """
            delta_Y = Y - Yalt

            return (delta_Y)

        def delta_x(L, Lalt, y):
            """
            method to calculate difference in q
            L = Leontief of baseline
            Lalt = Leontief of scenario
            """
            delta_x = (L-Lalt) @ y

            return (delta_x)

    def verifyIOT(S, Y, E):
        x_out = np.sum(np.array(S), axis=1) + np.sum(np.array(Y), axis=1)
        x_in = np.sum(S, axis=0) + np.sum(E[:9], axis=0)
        with np.errstate(divide="ignore", invalid="ignore"):
            ver = x_out/x_in * 100
        ver = np.nan_to_num(ver)
        return(ver)
