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
from scipy.linalg import lu_factor, lu_solve


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
        x = np.array(x, dtype=float)  # copy: never overwrite the caller's
        mask = (x == 0)
        x[~mask] = 1/x[~mask]
        return x

    def delta_Y(Y, Yalt):
        """
        method to calculate difference in Y
        Y = final demand baseline
        Yalt = final demand scenario
        """
        return Y - Yalt

    def delta_x(L, Lalt, y):
        """
        method to calculate difference in q
        L = Leontief of baseline
        Lalt = Leontief of scenario
        """
        return (L-Lalt) @ y

    def verifyIOT(S, Y, W):
        x_out = np.sum(np.array(S), axis=1) + np.sum(np.array(Y), axis=1)
        x_in = np.sum(S, axis=0) + np.sum(W[:9], axis=0)
        with np.errstate(divide="ignore", invalid="ignore"):
            ver = x_out/x_in * 100
        
        return np.nan_to_num(ver)

    class PxP_ITA_TC:
        """
        Model with Transformation Coefficients
        ProdxProd Industry Technology assumption
        """

        def T(V, inv_g):
            """
            Transformation matrix
            T = inv(diag(g)) * V
            """
            # V.transpose because it's in MAKE table instead of SUPPLY
            return np.asarray(V).transpose() * inv_g[:, None]

        def L(U, T, inv_q):
            """
            Input coefficients intermediates
            A = U * T * inv[diag (q)]

            Multiplier matrix
            L =  (I-A)^-1
            """
            A = (U @ T) * inv_q  # technical coefficient matrix
            A = np.nan_to_num(A)
            IA = np.identity(len(A)) - A
            return ln.inv(IA)

        def B(R, T, inv_q):
            """
            Calculates extension intensity
            """
            RT = R @ T
            return RT * inv_q  # Input coefficients

        def R(B, q):
            """
            Calculates absolute extensions
            """
            return np.asarray(B) * q

        def Z(T, U):
            """
            Intemediates
            Z = U * T
            """
            return U @ T

    class PxP_ITA_MSC:
        """
        Model with Market Share Coef.
        Prod x Prod Industry Technology assumption
        """
        def S(U, inv_g):
            """
            Intermediate coefficients
            Input requirements
            Z = U * inv(diag(g))
            """
            return np.asarray(U) * inv_g

        def D(V, inv_q):
            """
            Market share coefficients
            D = V * inv(diag(q))
            """
            # V.transpose because it's in MAKE table instead of SUPPLY
            return np.asarray(V).transpose() * inv_q

        def A(inter_coef, D):
            """
            Total requirement multipliers
            A = Z * D
            """
            return inter_coef @ D

        def L(A):
            """
            Leontief inverse
            L = (I-A)^-1
            """
            IA = np.identity(len(A)) - A
            return ln.inv(IA)

        def B(R, D, inv_g):
            """
            Calculates extensions intensities
            """
            return (np.asarray(R) * inv_g) @ D

        def R(B, q):
            """
            Calculates absolute extensions
            """
            return np.asarray(B) * q

        def Z(inter_coef, D, q):
            """
            Intermediates
            Z = inter_coef * D * diag(q)
            """
            return (inter_coef @ D) * q

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
            return np.asarray(Z).sum(axis=1) + np.asarray(Y).sum(axis=1)

        def B(R, inv_x):
            """
            Calculates extensions intensities
            """
            return np.asarray(R) * inv_x

        def R(B, x):
            """
            Calculates absolute extensions
            """
            return np.asarray(B) * x

        def x_IAy(L, y):
            """
            Total product ouput
            x = inv(I - A) * yi
            """
            return L @ y

        def x_solve(A, y):
            """
            Total product output without forming the Leontief inverse
            x = solve((I - A), y)
            """
            IA = -np.asarray(A)  # I - A, built in one n x n allocation
            IA[np.diag_indices_from(IA)] += 1
            return ln.solve(IA, np.asarray(y))

        def factorize(A):
            """
            LU factors of (I - A), to reuse across scenarios in x_update.
            A is overwritten.
            """
            IA = np.negative(A, out=A)
            IA[np.diag_indices_from(IA)] += 1
            return lu_factor(IA, overwrite_a=True, check_finite=False)

        def change_cover(D):
            """
            Rows R and columns C such that D is zero outside rows R and
            columns C, keeping len(R) + len(C) small. Rows are taken from the
            sparsest up: the k sparsest rows give C, the rest become R.
            """
            rows = np.flatnonzero(D.any(axis=1))
            if len(rows) == 0:
                return rows, rows
            B = D[rows] != 0
            order = np.argsort(B.sum(axis=1), kind="stable")
            B = B[order]
            touched = B.any(axis=0)
            first = np.argmax(B, axis=0)[touched]  # first sorted row per col
            n_cols = np.searchsorted(np.sort(first), np.arange(len(rows) + 1))
            k = np.argmin(n_cols + (len(rows) - np.arange(len(rows) + 1)))
            R = np.sort(rows[order[k:]])
            C = np.flatnonzero(touched)[first < k]
            return R, C

        def x_update(A, y, A0, lu0, max_rank=2000):
            """
            x = solve((I - A), y), reusing the LU factors lu0 of (I - A0).
            A0 is overwritten.

            A scenario changes A only in some rows R and columns C, so
            I - A = (I - A0) - U V' with U = [e_R, D[:, C] outside R],
            V' = [D[R, :]; e_C'], and the Woodbury identity gives x from
            len(R) + len(C) + 1 triangular solves instead of a new
            factorization. Falls back to a full solve when the rank is large
            or the update loses accuracy.
            """
            A = np.asarray(A)
            y = np.asarray(y, dtype=float)
            D = np.subtract(A, A0, out=A0)
            R, C = Operations.IOT.change_cover(D)
            z = lu_solve(lu0, y, check_finite=False)
            if len(R) + len(C) == 0:
                return z
            if len(R) + len(C) > max_rank:
                del D, A0
                return Operations.IOT.x_solve(A, y)

            U = np.zeros((len(A), len(R) + len(C)))
            U[R, np.arange(len(R))] = 1
            U[:, len(R):] = D[:, C]
            U[R, len(R):] = 0  # already covered by the rows in R
            DR = D[R]
            del D, A0
            MiU = lu_solve(lu0, U, overwrite_b=True, check_finite=False)
            VMiU = np.vstack([DR @ MiU, MiU[C]])
            Vz = np.concatenate([DR @ z, z[C]])
            x = z + MiU @ ln.solve(np.identity(len(Vz)) - VMiU, Vz)

            residual = y - (x - A @ x)
            if np.abs(residual).max() > 1e-9 * np.abs(x).max():
                return Operations.IOT.x_solve(A, y)
            return x

        def Z(A, x):
            """
            Total product ouput
            Z = A * diag_x
            """
            return np.asarray(A) * x

        def A(Z, inv_x):
            """
            Technical coefficient matrix
            A = Z * inv(diag(x))
            """
            return np.asarray(Z) * inv_x

        def L(A):
            """
            Leontief inverse
            L = (I-A)^-1
            """
            IA = np.identity(len(A)) - A
            return ln.inv(IA)

        def bY(RY, inv_yj):
            """
            Calculates intensities of extensions in final demand
            Method for transformation matrix of bY
            (e.g. final demand emissions)
            """
            return np.asarray(RY) * inv_yj

        def RY(bY, yj):
            """
            Caclculates absolute extensions in final demand
            """
            return np.asarray(bY) * yj

        # is this function really needed?
        def IOT(Z, Y, W, E, R, M):
            """
            IOT
            """
            x = Operations.IOT.x(Z, Y)  # total product output
            inv_x = Operations.inv(x)

            y = np.sum(Y, axis=1)

            A = Operations.IOT.A(Z, inv_x)  # technical coefficient matrix
            L = Operations.IOT.L(A)  # leontief inverse

            w = Operations.IOT.B(W, inv_x)  # primary inputs coef
            W = Operations.IOT.R(w, x)

            e = Operations.IOT.B(E, inv_x)  # Be coefficient matrix
            E = Operations.IOT.R(e, x)  # environmental extensions

            r = Operations.IOT.B(R, inv_x)  # Br coefficient matrix
            R = Operations.IOT.R(r, x)  # resource extensions

            m = Operations.IOT.B(M, inv_x)  # Bm coefficient matrix
            M = Operations.IOT.R(m, x)  # Material extension

            Z = Operations.IOT.Z(A, x)  # intermediates
            x = Operations.IOT.x_IAy(L, y)

            ver_base = Operations.verifyIOT(Z, Y, E)
            
            return {"A": A,
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

    def calculate_characterized(data):

        data.Cr_E = data.Cr_E_k @ data.E
        data.Cr_M = data.Cr_M_k @ data.M
        data.Cr_R = data.Cr_R_k @ data.R
        data.Cr_W = data.Cr_W_k @ data.W
        
        data.Cr_EY = data.Cr_E_k @ data.EY
        data.Cr_MY = data.Cr_M_k @ data.MY
        data.Cr_RY = data.Cr_R_k @ data.RY

        return data
