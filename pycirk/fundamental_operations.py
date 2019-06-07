# -*- coding: utf-8 -*-
"""
Created on Wed Nov 2 12:05:08 2016

Description: Class to perform SUT and IOT transformations and balancing

Scope: Modelling circular economy policies in EEIOA

@author:Franco Donati
@institution:Leiden University CML
"""
import numpy as np
from numpy import linalg as ln


class Operations:
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
        mask = (x == 0)
        x[~mask] = 1/x[~mask]

        return(x)

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

    def verifyIOT(S, Y, W):
        x_out = np.sum(np.array(S), axis=1) + np.sum(np.array(Y), axis=1)
        x_in = np.sum(S, axis=0) + np.sum(W[:9], axis=0)
        with np.errstate(divide="ignore", invalid="ignore"):
            ver = x_out/x_in * 100
        ver = np.nan_to_num(ver)
        return(ver)

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
            A = np.nan_to_num(A)
            IA = np.identity(len(A)) - A
            L = ln.inv(IA)

            return(L)

        def B(R, T, inv_diag_q):
            """
            Calculates extension intensity
            """
            RT = R @ T
            B = RT @ inv_diag_q  # Input coefficients
            return (B)

        def R(B, diag_q):
            """
            Calculates absolute extensions
            """
            R = B @ diag_q

            return (R)

        def Z(T, U):
            """
            Intemediates
            Z = U * T
            """
            Z = U @ T

            return(Z)

    class PxP_ITA_MSC:
        """
        Model with Market Share Coef.
        Prod x Prod Industry Technology assumption
        """
        # new update of numpy broke consistency of @ operator
        # where the exceptional behaviour appeared I substituted
        # @ with np.matmul(), this is to be changed in the future

        def S(U, inv_diag_g):
            """
            Intermediate coefficients
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

        def A(inter_coef, D):
            """
            Total requirement multipliers
            A = Z * D
            """
            A = np.matmul(inter_coef, D)
            return(A)

        def L(A):
            """
            Leontief inverse
            L = (I-A)^-1
            """
            IA = np.identity(len(A)) - A
            L = ln.inv(IA)

            return(L)

        def B(R, D, inv_diag_g):
            """
            Calculates extensions intensities
            """
            B_ = R @ inv_diag_g
            B = np.matmul(B_, D)
            return(B)

        def R(B, diag_q):
            """
            Calculates absolute extensions
            """
            R = B @ diag_q

            return(R)

        def Z(inter_coef, D, diag_q):
            """
            Intermediates
            Z = inter_coef * D * diag(q)
            """
            Z = np.matmul(inter_coef, D) @ diag_q

            return (Z)

    class IOT:
        """
        General IOT operations subclass
        some methods repeat from other subclasses
        but it's good to have them divided for clarity
        """

        def x(Z, Y):
            """
            total product output s the sum of Si and y
            """
            q = np.sum(np.array(Z), axis=1) + np.sum(np.array(Y), axis=1)

            return(q)

        def B(R, inv_diag_x):
            """
            Calculates extensions intensities
            """
            B = R @ inv_diag_x

            return(B)

        def R(B, diag_x):
            """
            Calculates absolute extensions
            """
            R = B @ diag_x

            return(R)

        def x_IAy(L, y):
            """
            Total product ouput
            x = inv(I - A) * yi
            """
            x = np.dot(L, y)

            return (x)

        def Z(A, diag_x):
            """
            Total product ouput
            Z = A * diag_x
            """
            Z = A @ diag_x

            return(Z)

        def A(Z, inv_diag_x):
            """
            Technical coefficient matrix
            A = Z * inv(diag(x))
            """
            A = Z @ inv_diag_x

            return(A)

        def L(A):
            """
            Leontief inverse
            L = (I-A)^-1
            """
            IA = np.identity(len(A)) - A
            L = ln.inv(IA)

            return(L)

        def bY(RY, inv_diag_yj):
            """
            Calculates intensities of extensions in final demand
            Method for transformation matrix of bY
            (e.g. final demand emissions)
            """
            bY = RY @ inv_diag_yj

            return(bY)

        def RY(bY, diag_yj):
            """
            Caclculates absolute extensions in final demand
            """
            RY = bY @ diag_yj

            return(RY)

        # is this function really needed?
        def IOT(Z, Y, W, E, R, M):
            """
            IOT
            """
            x = Operations.IOT.x(Z, Y)  # total product output
            diag_x = np.diag(x)
            inv_diag_x = Operations.inv(diag_x)

            y = np.sum(Y, axis=1)

            A = Operations.IOT.A(Z, inv_diag_x)  # technical coefficient matrix
            L = Operations.IOT.L(A)  # leontief inverse

            w = Operations.IOT.B(W, inv_diag_x)  # primary inputs coef
            W = Operations.IOT.R(w, diag_x)

            e = Operations.IOT.B(E, inv_diag_x)  # Be coefficient matrix
            E = Operations.IOT.R(e, diag_x)  # environmental extensions

            r = Operations.IOT.B(R, inv_diag_x)  # Br coefficient matrix
            R = Operations.IOT.R(r, diag_x)  # resource extensions

            m = Operations.IOT.B(M, inv_diag_x)  # Bm coefficient matrix
            M = Operations.IOT.R(m, diag_x)  # Material extension

            Z = Operations.IOT.Z(A, diag_x)  # intermediates
            x = Operations.IOT.x_IAy(L, y)

            ver_base = Operations.verifyIOT(Z, Y, E)

            IOT = {"A": A,
                   "Z": Z,
                   "L": L,
                   "Z": Z,
                   "Y": Y,
                   "w": w,
                   "W": W,
                   "x": x,
                   "E": E,
                   "e": e,
                   "R": R,
                   "r": r,
                   "M": M,
                   "m": m,
                   "ver_base": ver_base
                   }

            return(IOT)

    def calculate_characterized(data):

        data.Cr_E = data.Cr_E_k @ data.E
        data.Cr_M = data.Cr_M_k @ data.M
        data.Cr_R = data.Cr_R_k @ data.R
        data.Cr_W = data.Cr_W_k @ data.W

        data.Cr_EY = data.Cr_E_k @ data.EY
        data.Cr_MY = data.Cr_M_k @ data.MY
        data.Cr_RY = data.Cr_R_k @ data.RY

        data.Cr_tot_E = data.Cr_E.sum(axis=1) + data.Cr_EY.sum(axis=1)
        data.Cr_tot_M = data.Cr_M.sum(axis=1) + data.Cr_MY.sum(axis=1)
        data.Cr_tot_R = data.Cr_R.sum(axis=1) + data.Cr_RY.sum(axis=1)

        return(data)
