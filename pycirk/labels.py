# -*- coding: utf-8 -*-
"""
Created on sat Jan 28 2017

Description: Labelling elements for SUTs and IOTs

Scope: Modelling the Circular Economy in EEIO

@author:Franco Donati
@institution:Leiden University CML
"""

from pandas import DataFrame as df
from pandas import MultiIndex as mi
import munch
import numpy as np
import warnings


def save_labels( data):
    get_labels(data["V"], 1).to_csv("labels//industry.csv", index=False)  # with unit column
    get_labels(data["Y"], 0).to_csv("labels//products.csv", index=False)  # with unit column
    get_labels(data["CrBe"], 0).to_csv("labels//charact_emissions.csv", index=False)
    get_labels(data["CrBr"], 0).to_csv("labels//charact_resources.csv", index=False)
    get_labels(data["CrBm"], 0).to_csv("labels//charact_materials.csv", index=False)
    get_labels(data["CrE"], 0).to_csv("labels//charact_factor_inputs.csv", index=False)

    # without unit column = to be used for extension tables
    get_labels(data["Y"], 0, drop_unit=True)

    get_labels(data["E"], 0).to_csv("labels//factor_inputs.csv", index=False)
    get_labels(data["Y"], 1).to_csv("labels//final_demand.csv", index=False)
    get_labels(data["Y"], 1, drop_unit=True)
    get_labels(data["Be"], 0).to_csv("labels//emissions.csv", index=False)
    get_labels(data["Br"], 0).to_csv("labels//resources.csv", index=False)
    get_labels(data["Bm"], 0).to_csv("labels//materials.csv", index=False)

def load_labels( data):


def relabel_in_bulk( data):
    """
    This function makes sure that everything is labeled in IOT tables
    """

    # Relabel Main IOT elements
    data.S = relabel(data["S"], prod_get_l, prod_get_l_m, "S")
    data.L = relabel(data["L"], prod_get_l, prod_get_l, "L")
    data.A = relabel(data["A"], prod_get_l_m, prod_get_l_m, "A")
    data.Y = relabel(data["Y"], Y_get_l, prod_get_l_m, "Y")
    data.E = relabel(data["E"], prod_get_l, E_get_l, "E")
    data.RE = relabel(data["RE"], prod_get_l_m, E_get_l, "RE")

    # Relabel Inter-trans extensions
    data.Be = relabel(data["Be"], prod_get_l, Be_get_l, "Be")
    data.Br = relabel(data["Br"], prod_get_l, Br_get_l, "Br")
    data.Bm = relabel(data["Bm"], prod_get_l, Bm_get_l, "Bm")

    # Inter-trans extensions' intensities
    data.RBe = relabel(data["RBe"], prod_get_l_m, Be_get_l, "RBe")
    data.RBr = relabel(data["RBr"], prod_get_l_m, Br_get_l, "RBr")
    data.RBm = relabel(data["RBm"], prod_get_l_m, Bm_get_l, "RBm")

    # Relabel characterisation
    data.CrBe = relabel(data["CrBe"], prod_get_l, CrBe_get_l, "CrBe")
    data.CrBr = relabel(data["CrBr"], prod_get_l, CrBr_get_l, "CrBe")
    data.CrBm = relabel(data["CrBm"], prod_get_l, CrBm_get_l, "CrBe")
    data.CrE = relabel(data["CrE"], prod_get_l, CrE_get_l, "CrBe")

    # label q
    data.x = relabel(data["x"], "x", prod_get_l_m, "x")
    # label balance verification
    data.ver_label = "balance (x_out/x_in) - % - 100=balanced - 0=NaN no values"
    data.ver = relabel(df(data["ver"], ver_label, prod_get_l, "ver"))

    # Labeling final demand extensions
    data.YBe = relabel(data["YBe"], Y_get_l, Be_get_l, "YBe")

    data.YBr = relabel(data["YBr"], Y_get_l, Br_get_l, "YBr")

    data.YBm = relabel(data["YBm"], Y_get_l, Bm_get_l, "YBm")

    # Labeling final demand extensions' intensities
    data.RYBe = relabel(data["RYBe"], Y_get_l_m, Be_get_l, "RYBe")
    data.RYBr = relabel(data["RYBr"], Y_get_l_m, Br_get_l, "RYBr")
    data.RYBm = relabel(data["RYBm"], Y_get_l_m, Bm_get_l, "RYBm")

    # Relabel characterisation for final demand
    data.CrYBe = relabel(data["CrYBe"], Y_get_l, CrBe_get_l, "CrBe")
    data.CrYBr = relabel(data["CrYBr"], Y_get_l, CrBr_get_l, "CrBe")
    data.CrYBm = relabel(data["CrYBm"], Y_get_l, CrBm_get_l, "CrBe")

    return(data)

def get_labels( matrix, axis=0, drop_unit=False):
    """
    Collects labels from a dataframe
    axis = 0 => Index
    axis = 1 => columns
    """
    if axis == 0:  # collects index
        try:
            output = matrix.index.to_frame(index=False)

            # print("ind",matrix.index[0])
        except Exception:
            # this exception is here only in the case the multi-index is set up
            # as a list of flat strings instead of an actual multi-index
            output = df(list(matrix.index)).copy()
    elif axis == 1:  # collects columns
        try:
            output = matrix.columns.to_frame(index=False)
#            print("col",matrix.index[0])
        except Exception:
            output = df(list(matrix.columns)).copy()

    if drop_unit is True:
        try:
            output = output.drop(["unit"], axis=1)
        except ValueError:
            try:
                output = output.drop(["unit"], axis=0)
            except ValueError:
                warnings.warn("issue dropping 'unit' labels, ignore warning" +
                              "unless you want to fix it")
    else:
        pass

    return(output)

def apply_labels( matrix, labels, axis=0):
    """
    Applies labels to a dataframe
    axis = 0 => Index
    axis = 1 => columns
    """
    if axis == 0:  # apply index
        matrix.index = mi.from_arrays(labels.values.T)
        matrix.index.names = labels.columns
    elif axis == 1:  # collects columns
        matrix.columns = mi.from_arrays(labels.values.T)
        matrix.columns.names = labels.columns

    return(matrix)

def relabel( M, column_labels, index_labels, name):
    """
    Processes apply_labels and apply _names together
    """
    M = df(M)

    try:
        M = apply_labels(M, column_labels, axis=1)  # columns
    except Exception:
        # in case a string is passed for column label for a vector
        M.columns = [column_labels]
    M = apply_labels(M, index_labels, axis=0)  # index

    return(M)
