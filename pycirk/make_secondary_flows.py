#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 16 15:10:19 2018
Description: Modifying SUT to ensure appearance of secondary material flows in
IOT

Scope: Modelling the Circular Economy in EEIO

@author:Franco Donati
@institution:Leiden University CML
"""
import numpy as np
from pycirk.labels import positions


def make_secondary(data):
    """
    This allows to allign secondary flow in such a way that they then
    appear in the IOT
    """
    V = data["V"]
    U = data["U"]
    Y = data["Y"]

    materials = ["_WOOD", "_PULP", "_PLAS", "_GLAS", "_CMNT", "_STEL",
                 "_PREM", "_ALUM", "_LZTP", "_COPP", "_ONFM", "_CONS"]

    for l in materials:
        prod_or = "C" + l
        ind_or = "A" + l
        moved = allocate_sec_mat(V, U, Y, prod_or, ind_or)
        V = moved["V"]
        U = moved["U"]

    data["V"] = V
    data["U"] = U

    return(data)


def allocate_sec_mat(V, U, Y, prod_or, ind_or):
    """
    This function allows to move the primary material output from the
    secondary material industries to the secondary material output.
    This allows for the presence of secondary materials in the IOT
    once they are transformed from SUTS.

    prod_or = row position of the primary supplied material
    ind_or = colum pos. of the primary industry supplying primary material
    """
    V = V.copy()
    U = U.copy()
    Y = Y.copy()

    index = V.index.to_frame(False)
    columns = V.columns.to_frame(False)

    reg = None

    # position of the primary material
    or_prod_ix_pos = positions(index, reg, prod_or)
    or_ind_col_pos = positions(columns, reg, ind_or)

    # position of the secondary material
    des_prod_ix_pos = or_prod_ix_pos + 1
    des_ind_col_pos = or_ind_col_pos + 1

    # getting the value of secondary material from the supply table
    # which is placed on the primary material row
    misplaced = np.array(V.iloc[or_prod_ix_pos, des_ind_col_pos])

    # placing the misplaced value to the secondary material row
    V.iloc[des_prod_ix_pos, des_ind_col_pos] = misplaced

    # collecting how much of the primary material is consumed by final demand
    # to be subtracted from the supply value
    Y_values = np.sum(Y.iloc[or_prod_ix_pos], axis=1)

    # how the supply to intraindustry transactions is distributed in its use
    dist = np.dot(np.diag(1/(np.sum(V.iloc[or_prod_ix_pos], axis=1)-Y_values)),
                  U.iloc[or_prod_ix_pos])

    # mapping the use of the secondary material according to the distribution
    # of use of the primary material
    U.iloc[des_prod_ix_pos] = np.diag(misplaced.sum(axis=1)) @ dist

    # subtracting the use of secondary material from the primary
    U.iloc[or_prod_ix_pos] = np.subtract(U.iloc[or_prod_ix_pos],
                                         np.array(U.iloc[des_prod_ix_pos]))

    # zeroing the misplaced value of secondary materials
    V.iloc[or_prod_ix_pos, des_ind_col_pos] = 0

    # verifying balance
    g1_over_g2 = (np.sum(V, axis=1) / (np.sum(U, axis=1) +
                                       np.sum(Y, axis=1))) * 100

    output = {"V": V,
              "U": U,
              "balance": g1_over_g2}

    return(output)
