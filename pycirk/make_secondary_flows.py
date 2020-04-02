#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 16 15:10:19 2018
Description: Modifying SUT to ensure appearance of secondary material flows in
IOT

Scope: Modelling the Circular Economy in EEIO

@author:Franco Donati
@contributor: Arjan de Koning
@institution:Leiden University CML
"""
import numpy as np
import pycirk.positions as pos


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

    prod_or = pos.make_coord_array_for_make_sec(products, no_countries, 200)
    ind_or = pos.make_coord_array_for_make_sec(industries, no_countries, 163)

    moved = allocate_sec_mat(V, U, Y, prod_or, ind_or)

    V = moved["V"]
    U = moved["U"]

    data["V"] = V
    data["U"] = U

    return data


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
    misplaced = V.iloc[prod_or, des_ind_col_pos]
    
    # placing the misplaced value to the secondary material row
    V.iloc[des_prod_ix_pos, des_ind_col_pos] = np.array(misplaced)

    # collecting how much of the primary material is consumed by final demand
    # to be subtracted from the supply value

    # matrix  of primary sectors x all products (588 x 7987)
    prim_sec_supply_trans = V.iloc[prod_or]

    # scalar value of sum total primary industry supply
    # prim_sec_tot_output = np.sum(prim_sec_supply_trans)
    prim_sec_tot_output = prim_sec_supply_trans.sum(axis=1)

    # matrix of secondary product supply by secondary industry (588 x 588)
    sec_supply_trans = V.iloc[des_prod_ix_pos, des_ind_col_pos]

    # vector of total secondary industry output (588)
    sec_output = sec_supply_trans.sum(axis=1)
    # vector of ratios between secondary output per industry and sum total
    # industry supply (diagonalised 588  x 588)
    ratio_prim_sec = np.zeros((len(sec_output)))
    for idx in range(0, len(sec_output)):
        if prim_sec_tot_output.iloc[idx] != 0:
            ratio_prim_sec[idx] = np.array(sec_output.iloc[idx] / prim_sec_tot_output.iloc[idx])
    ratio_prim_sec = np.diag(ratio_prim_sec)

    prim_sec_use_trans = U.iloc[prod_or]

    prim_sec_fin_dem_trans = Y.iloc[prod_or]

    eye = np.identity(len(ratio_prim_sec))

    U.iloc[prod_or] = (eye - ratio_prim_sec) @ np.array(prim_sec_use_trans)

    U.iloc[des_prod_ix_pos] = ratio_prim_sec @ np.array(prim_sec_use_trans)

    Y.iloc[prod_or] = (eye - ratio_prim_sec) @ np.array(prim_sec_fin_dem_trans)

    Y.iloc[des_prod_ix_pos] = ratio_prim_sec @ np.array(prim_sec_fin_dem_trans)

    V.iloc[prod_or, des_ind_col_pos] = 0

    print('splitting off secondary materials completed')

    return {"V": V,
            "U": U,
            "Y": Y}
