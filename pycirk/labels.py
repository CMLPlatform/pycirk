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
