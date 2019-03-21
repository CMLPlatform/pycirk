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
from pandas import read_csv
from munch import Munch
import warnings


def save_labels(data):
    
    try:
        get_labels(data["V"], 1).to_csv("pycirk//labels//industry.csv", index=False)  # with unit column
    except Exception:
        pass
    
    get_labels(data["Y"], 0).to_csv("pycirk//labels//products.csv", index=False)  # with unit column
    get_labels(data["CrBe"], 0).to_csv("pycirk//labels//charact_emissions.csv", index=False)
    get_labels(data["CrBr"], 0).to_csv("pycirk//labels//charact_resources.csv", index=False)
    get_labels(data["CrBm"], 0).to_csv("pycirk//labels//charact_materials.csv", index=False)
    get_labels(data["CrE"], 0).to_csv("pycirk//labels//charact_factor_inputs.csv", index=False)
    get_labels(data["E"], 0).to_csv("pycirk//labels//factor_inputs.csv", index=False)
    get_labels(data["Y"], 1).to_csv("pycirk//labels//final_demand.csv", index=False)
    get_labels(data["Be"], 0).to_csv("pycirk//labels//emissions.csv", index=False)
    get_labels(data["Br"], 0).to_csv("pycirk//labels//resources.csv", index=False)
    get_labels(data["Bm"], 0).to_csv("pycirk//labels//materials.csv", index=False)

def load_labels():
    
    try:
        ind = read_csv("pycirk//labels//industry.csv")  # with unit column
        prod = None
    except Exception:
        prod = read_csv("pycirk//labels//products.csv")  # with unit column
        ind = None

    primary = read_csv("pycirk//labels//factor_inputs.csv")
    fin_dem = read_csv("pycirk//labels//final_demand.csv")
    emis = read_csv("pycirk//labels//emissions.csv")
    res = read_csv("pycirk//labels//resources.csv")
    mat = read_csv("pycirk//labels//materials.csv")

    car_emis = read_csv("pycirk//labels//charact_emissions.csv")
    car_res = read_csv("pycirk//labels//charact_resources.csv")
    car_mat = read_csv("pycirk//labels//charact_materials.csv")
    car_prim = read_csv("pycirk//labels//charact_factor_inputs.csv")

    labels = {"ind": ind,
              "prod": prod,
              "primary": primary,
              "fin_dem": fin_dem,
              "emis": emis,
              "res": res,
              "mat": mat,
              "car_emis": car_emis,
              "car_res": car_res,
              "car_mat": car_mat,
              "car_prim": car_prim}
    return(labels)


def relabel_in_bulk(data, trans_method=0):
    """
    This function makes sure that everything is labeled in IOT tables

    trans_method = 0 is prod x prod , 1 is ind x ind
    """
    lb = Munch(load_labels())

    if trans_method == 0:
        cat = lb.prod
    elif trans_method == 1:
        cat = lb.ind

    # Relabel Main IOT elements
    data.S = relabel(data.S, cat.iloc[:, :4], cat, "S")
    data.L = relabel(data.L, cat.iloc[:, :4], cat.iloc[:, :4], "L")
    data.A = relabel(data.A, cat, cat, "A")
    data.Y = relabel(data.Y, lb.fin_dem, cat, "Y")
    data.E = relabel(data.E, cat.iloc[:, :4], lb.primary, "E")
    data.RE = relabel(data.RE, cat, lb.primary, "RE")

    # Relabel Inter-trans extensions
    data.Be = relabel(data.Be, cat.iloc[:, :4], lb.emis, "Be")
    data.Br = relabel(data.Br, cat.iloc[:, :4], lb.res, "Br")
    data.Bm = relabel(data.Bm, cat.iloc[:, :4], lb.mat, "Bm")

    # Inter-trans extensions' intensities
    data.RBe = relabel(data.RBe, cat, lb.emis, "RBe")
    data.RBr = relabel(data.RBr, cat, lb.res, "RBr")
    data.RBm = relabel(data.RBm, cat, lb.mat, "RBm")

    # Relabel characterisation
    data.CrBe = relabel(data.CrBe, cat.iloc[:, :4], lb.car_emis, "CrBe")
    data.CrBr = relabel(data.CrBr, cat.iloc[:, :4], lb.car_res, "CrBe")
    data.CrBm = relabel(data.CrBm, cat.iloc[:, :4], lb.car_mat, "CrBe")
    data.CrE = relabel(data.CrE, cat.iloc[:, :4], lb.car_prim, "CrBe")

    # label q
    data.x = relabel(data.x, "x", cat, "x")
    # label balance verification
    ver_label = "balance (x_out/x_in) - % - 100=balanced - 0=NaN no values"
    data.ver_base = relabel(data.ver_base, ver_label, cat.iloc[:, :4], "ver_base")

    # Labeling final demand extensions
    data.YBe = relabel(data.YBe, lb.fin_dem.iloc[:, :4], lb.emis, "YBe")

    data.YBr = relabel(data.YBr, lb.fin_dem.iloc[:, :4], lb.res, "YBr")

    data.YBm = relabel(data.YBm, lb.fin_dem.iloc[:, :4], lb.mat, "YBm")

    # Labeling final demand extensions' intensities
    data.RYBe = relabel(data.RYBe, lb.fin_dem, lb.emis, "RYBe")
    data.RYBr = relabel(data.RYBr, lb.fin_dem, lb.res, "RYBr")
    data.RYBm = relabel(data.RYBm, lb.fin_dem, lb.mat, "RYBm")

    # Relabel characterisation for final demand
    data.CrYBe = relabel(data.CrYBe, lb.fin_dem, lb.car_emis, "CrBe")
    data.CrYBr = relabel(data.CrYBr, lb.fin_dem, lb.car_res, "CrBe")
    data.CrYBm = relabel(data.CrYBm, lb.fin_dem, lb.car_mat, "CrBe")

    return(data)


def get_labels(matrix, axis=0, drop_unit=False):
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


def apply_labels(matrix, labels, axis=0):
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


def relabel(M, column_labels, index_labels, name):
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
