# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 18:10:44 2019

@author: donatif
"""

import numpy as np


def sherman_morrison(A, L, coefficient, coor_s, coor_m):

    IA = np.identity(A) - A

    u = np.zeros(len(L))
    v = np.zeros(len(L))

    ones = np.ones(len(L), dtype=int)

    u[coor_s] = coefficient

    for l in coor_s:
        v = IA[l]
        v[~coor_m] = 0
        v = np.diag(-v)
        u = np.diag(u)
        uv = u @ ones @ v

        sher_mor = L - ((uv @ v) * L) / (1 + v @ L @ u)

    return(sher_mor)

# error=max(max(inv_new_L_default-inv_new_L_Sherman_Morrison))
