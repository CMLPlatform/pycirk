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
# from pycirk.labels import positions


def make_secondary(data):
    """
    This allows to allign secondary flow in such a way that they then
    appear in the IOT

    Primary Products' positions

    C_WOOD: 57
    C_PULP: 59
    C_PLAS: 85
    C_GLAS: 96
    C_CMNT: 100
    C_STEL: 103
    C_PREM: 105
    C_ALUM: 107
    C_LZTP: 109
    C_COPP: 111
    C_ONFM: 113
    C_CONS: 149

    Primary Sectors'positions:

    A_WOOD: 49
    A_PULP: 51
    A_PLAS: 58
    A_GLAS: 64
    A_CMNT: 68
    A_STEL: 71
    A_PREM: 73
    A_ALUM: 75
    A_LZTP: 77
    A_COPP: 79
    A_ONFM: 81
    A_CONS: 112

    """
    V = data["V"]
    U = data["U"]
    Y = data["Y"]

    products = np.array([57, 59, 85, 96, 100, 103,
                         105, 107, 109, 111, 113, 149])

    industries = np.array([49, 51, 58, 64, 68, 71, 73,
                           75, 77, 79, 81, 112])

    no_countries = int(len(Y)/200)

    prod_or = make_coord_array(products, no_countries, 200)
    ind_or = make_coord_array(industries, no_countries, 163)

    moved = allocate_sec_mat(V, U, Y, prod_or, ind_or)

    V = moved["V"]
    U = moved["U"]

    data["V"] = V
    data["U"] = U

    return(data)


def make_coord_array(coordinates, no_countries, no_ind_or_prod):

    n = 0
    nn = 0
    while n in range(len(coordinates)):
        while nn in range(no_countries):
            g = coordinates + no_ind_or_prod*nn
            if "s" not in locals():
                s = g
            else:
                s = np.concatenate([s, g])
            nn = nn+1
        n = n+1

    return(s)


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

    # position of the secondary material
    des_prod_ix_pos = prod_or + 1
    des_ind_col_pos = ind_or + 1

    # getting the value of secondary material from the supply table
    # which is placed on the primary material row
    misplaced = np.array(V.iloc[prod_or, des_ind_col_pos])

    # placing the misplaced value to the secondary material row
    V.iloc[des_prod_ix_pos, des_ind_col_pos] = misplaced

    # collecting how much of the primary material is consumed by final demand
    # to be subtracted from the supply value
    Y_values = np.sum(Y.iloc[prod_or], axis=1)

    # how the supply to intraindustry transactions is distributed in its use
    dist = np.dot(np.diag(1/(np.sum(V.iloc[prod_or], axis=1)-Y_values)),
                  U.iloc[prod_or])

    # mapping the use of the secondary material according to the distribution
    # of use of the primary material
    U.iloc[des_prod_ix_pos] = np.diag(misplaced.sum(axis=1)) @ dist

    # subtracting the use of secondary material from the primary
    U.iloc[prod_or] = np.subtract(U.iloc[prod_or],
                                  np.array(U.iloc[des_prod_ix_pos]))

    # zeroing the misplaced value of secondary materials
    V.iloc[prod_or, des_ind_col_pos] = 0

    # verifying balance
    g1_over_g2 = (np.sum(V, axis=1) / (np.sum(U, axis=1) +
                                       np.sum(Y, axis=1))) * 100

    output = {"V": V,
              "U": U,
              "balance": g1_over_g2}

    return(output)



# =============================================================================
# def make_secondary(data):
#     """
#     This allows to allign secondary flow in such a way that they then
#     appear in the IOT
#     """
#     V = data["V"]
#     U = data["U"]
#     Y = data["Y"]
# 
#     materials = ["_WOOD", "_PULP", "_PLAS", "_GLAS", "_CMNT", "_STEL",
#                  "_PREM", "_ALUM", "_LZTP", "_COPP", "_ONFM", "_CONS"]
# 
#     for l in materials:
#         prod_or = "C" + l
#         ind_or = "A" + l
#         moved = allocate_sec_mat(V, U, Y, prod_or, ind_or)
#         V = moved["V"]
#         U = moved["U"]
# 
#     data["V"] = V
#     data["U"] = U
# 
#     return(data)
# 
# 
# def allocate_sec_mat(V, U, Y, prod_or, ind_or):
#     """
#     This function allows to move the primary material output from the
#     secondary material industries to the secondary material output.
#     This allows for the presence of secondary materials in the IOT
#     once they are transformed from SUTS.
# 
#     prod_or = row position of the primary supplied material
#     ind_or = colum pos. of the primary industry supplying primary material
#     """
#     V = V.copy()
#     U = U.copy()
#     Y = Y.copy()
# 
#     index = V.index.to_frame(False)
#     columns = V.columns.to_frame(False)
# 
#     reg = None
# 
#     # position of the primary material
#     or_prod_ix_pos = positions(index, reg, prod_or)
#     or_ind_col_pos = positions(columns, reg, ind_or)
# 
#     # position of the secondary material
#     des_prod_ix_pos = or_prod_ix_pos + 1
#     des_ind_col_pos = or_ind_col_pos + 1
# 
#     # getting the value of secondary material from the supply table
#     # which is placed on the primary material row
#     misplaced = np.array(V.iloc[or_prod_ix_pos, des_ind_col_pos])
# 
#     # placing the misplaced value to the secondary material row
#     V.iloc[des_prod_ix_pos, des_ind_col_pos] = misplaced
# 
#     # collecting how much of the primary material is consumed by final demand
#     # to be subtracted from the supply value
#     Y_values = np.sum(Y.iloc[or_prod_ix_pos], axis=1)
# 
#     # how the supply to intraindustry transactions is distributed in its use
#     dist = np.dot(np.diag(1/(np.sum(V.iloc[or_prod_ix_pos], axis=1)-Y_values)),
#                   U.iloc[or_prod_ix_pos])
# 
#     # mapping the use of the secondary material according to the distribution
#     # of use of the primary material
#     U.iloc[des_prod_ix_pos] = np.diag(misplaced.sum(axis=1)) @ dist
# 
#     # subtracting the use of secondary material from the primary
#     U.iloc[or_prod_ix_pos] = np.subtract(U.iloc[or_prod_ix_pos],
#                                          np.array(U.iloc[des_prod_ix_pos]))
# 
#     # zeroing the misplaced value of secondary materials
#     V.iloc[or_prod_ix_pos, des_ind_col_pos] = 0
# 
#     # verifying balance
#     g1_over_g2 = (np.sum(V, axis=1) / (np.sum(U, axis=1) +
#                                        np.sum(Y, axis=1))) * 100
# 
#     output = {"V": V,
#               "U": U,
#               "balance": g1_over_g2}
# 
#     return(output)
# 
# =============================================================================
