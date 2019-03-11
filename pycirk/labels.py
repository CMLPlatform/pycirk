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
import numpy as np
import warnings


class Labels:

    def __init__(self, data):
        # Collecting and saving labels to be used by labels.py
        self.ind_get_l_m = get_labels(data["V"], 1).to_csv("labels//industry.csv", index=False)  # with unit column
        self.prod_get_l_m = get_labels(data["Y"], 0).to_csv("labels//products.csv", index=False)  # with unit column
        self.CrBe_get_l = get_labels(data["CrBe"], 0).to_csv("labels//charact_emissions.csv", index=False)
        self.CrBr_get_l = get_labels(data["CrBr"], 0).to_csv("labels//charact_resources.csv", index=False)
        self.CrBm_get_l = get_labels(data["CrBm"], 0).to_csv("labels//charact_materials.csv", index=False)
        self.CrE_get_l = get_labels(data["CrE"], 0).to_csv("labels//charact_factor_inputs.csv", index=False)

        # without unit column = to be used for extension tables
        self.prod_get_l = get_labels(data["Y"], 0, drop_unit=True)

        self.E_get_l = get_labels(data["E"], 0).to_csv("labels//factor_inputs.csv", index=False)
        self.Y_get_l_m = get_labels(data["Y"], 1).to_csv("labels//final_demand.csv", index=False)
        self.Y_get_l = get_labels(data["Y"], 1, drop_unit=True)
        self.Be_get_l = get_labels(data["Be"], 0).to_csv("labels//emissions.csv", index=False)
        self.Br_get_l = get_labels(data["Br"], 0).to_csv("labels//resources.csv", index=False)
        self.Bm_get_l = get_labels(data["Bm"], 0).to_csv("labels//materials.csv", index=False)
        del(data)

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
        ver = relabel(df(data["ver"], ver_label, self.prod_get_l, "ver"))

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


def bireg_labels(matrix):

    index = get_labels(matrix, 0)
    columns = get_labels(matrix, 1)

    try:
        index = index.drop("country", axis=1)
    except Exception:
        print("The index labels are not country specific")
        pass

    try:
        columns = columns.drop("country", axis=1)
    except Exception:
        print("The columns labels are not country specific")
        pass

    labels = {"ind": index, "col": columns}

    return(labels)


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


def positions(ind_df, reg, cat):
    """
    Takes a dataframe of the multiindex and identifies the position
    of the specified values

    reg = regions [EU or ROW]
    cat = category of synonym [C_STEL]

    """
# =============================================================================
#     Should be expanded to include also other multindex elements so to allow
#     for more flexibility in label management
# =============================================================================

    if "region" in ind_df.columns:
        # this exception is added for indeces that do not have a regional label
        try:
            if reg not in ["All", "None", "", "nan"]:
                if reg in ["EU", "ROW"]:
                    ind_df = ind_df.loc[ind_df["region"] == reg]
                else:
                    try:
                        ind_df = ind_df.loc[ind_df["country_code"] == reg]
                    except Exception:
                        pass
            else:
                reg = range(len(ind_df))
        except Exception:
            pass
    else:
        pass

    try:
        if cat not in ["All", "None", "", "nan"]:
            try:
                ind_df = ind_df.loc[ind_df["synonym"] == cat]
            except Exception:
                ind_df = ind_df.loc[ind_df["characterization"] == cat]
        else:
            cat = range(len(ind_df))
    except Exception:
        pass

    positions = np.array(ind_df.index)

    return(positions)
