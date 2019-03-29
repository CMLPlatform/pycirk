# -*- coding: utf-8 -*-
"""
Created on Fri Nov 25 12:13:29 2016

Description: Reading policy values and modifying matrices for scenarios

Scope: Modelling the Circular Economy in EEIO

@author: Franco Donati
@institution: Leiden University CML
"""

import pandas as pd
import numpy as np
from pycirk import positions
from pycirk.fundamental_operations import Operations as ops
from copy import deepcopy
import warnings
# from pycirk import sherman_morrison as sher_mor


def make_counterfactuals(data, scen_no, scen_file, labels):
    """
    Calculate all the counterfactual matrices for the database
    """
    data = deepcopy(data)

    # Apply policy to economic matrices
    data.S = counterfactual(scen_file, scen_no, data.S, "S", labels)

    # First total product output from changes in S
    x_ = ops.IOT.x(data.S, data.Y)
    diag_x_ = np.diag(x_)
    inv_diag_x_ = ops.inv(diag_x_)

    A = ops.IOT.A(data.S, inv_diag_x_)

    diag_yj = np.diag(data.Y.sum(axis=0))

    data.A = counterfactual(scen_file, scen_no, A, "A", labels)
    data.Y = counterfactual(scen_file, scen_no, data.Y, "Y", labels)

    x = ops.IOT.x(data.S, data.Y)
    diag_x = np.diag(x)
    inv_diag_x = ops.inv(diag_x)

    data.w = counterfactual(scen_file, scen_no, data.w, "w", labels)

    W = ops.IOT.R(data.w, diag_x)
    data.W = counterfactual(scen_file, scen_no, W, "W", labels)

    # Apply policy to intermediate extension coefficient matrices
    data.e = counterfactual(scen_file, scen_no, data.e, "e", labels)
    data.r = counterfactual(scen_file, scen_no, data.r, "r", labels)
    data.m = counterfactual(scen_file, scen_no, data.m, "m", labels)

    # Apply policy to intermediate extension matrices
    E = ops.IOT.R(data.E, diag_x)
    R = ops.IOT.R(data.R, diag_x)
    M = ops.IOT.R(data.M, diag_x)

    data.E = counterfactual(scen_file, scen_no, E, "E", labels)
    data.R = counterfactual(scen_file, scen_no, R, "R", labels)
    data.M = counterfactual(scen_file, scen_no, M, "M", labels)

    # Apply policy to  final demand extension coefficient matrices
    data.Ye = counterfactual(scen_file, scen_no, data.Ye, "Ye", labels)
    data.Yr = counterfactual(scen_file, scen_no, data.Yr, "Yr", labels)
    data.Ym = counterfactual(scen_file, scen_no, data.Ym, "Ym", labels)

    # Apply policy to final demand extension matrices
    YE = ops.IOT.YR(data.Ye, diag_x)
    YR = ops.IOT.YR(data.Yr, diag_x)
    YM = ops.IOT.YR(data.Ym, diag_x)

    data.YE = counterfactual(scen_file, scen_no, YE, "YE", labels)
    data.YR = counterfactual(scen_file, scen_no, YR, "YR", labels)
    data.YM = counterfactual(scen_file, scen_no, YM, "YM", labels)

    # Scenario
    data.L = ops.IOT.L(data.A)  # L from S and Y modified
    diag_yj = np.diag(data.Y.sum(axis=0))  # column sum of FD
    inv_diag_yj = ops.inv(diag_yj)
    yi = np.sum(data.Y, axis=1)  # row sum of final demand
    data.x = ops.IOT.x_IAy(data.L, yi)
    diag_x = np.diag(data.x)

    data.S = ops.IOT.S(data.A, diag_x)

    data.w = ops.IOT.B(data.W, inv_diag_x)  # primary inputs coef
    data.e = ops.IOT.B(data.E, inv_diag_x)  # emissions ext coef
    data.r = ops.IOT.B(data.R, inv_diag_x)  # resource ext coef
    data.m = ops.IOT.B(data.M, inv_diag_x)  # material ext coef

    data.Ye = ops.IOT.B(data.YE, inv_diag_yj)  # emissions ext FD coef
    data.Yr = ops.IOT.B(data.YR, inv_diag_yj)  # resource ext FD coef
    data.Ym = ops.IOT.B(data.YM, inv_diag_yj)  # material ext FD coef

    return(data)


def counterfactual(scen_file, scen_no, M, M_name, labels):
    """
    Separates policy interventions by matrix subject to intervention
    and aply policy interventions on specific matrix

    scen_no = specific scenario e.g "1" or "scenario_1"
    M = matrix affected by the policies
    M_name = matrix name as diplayed under sheet_name["matrix"]
    """

    if type(scen_no) is int:
        scen_no = "scenario_" + str(scen_no)

    elif scen_no.startswith("scenario_"):
        pass
    else:
        raise KeyError("only integer or explicit name (scenario_x)" +
                       "are allowed")

    scenario = pd.read_excel(scen_file, sheet_name=scen_no, header=1,
                             index=None)

    if scenario["matrix"].isnull().values.all():
        matrix = M
        warnings.warn("\n\nA scenario sheet was found but no parameters" +
                      "were set, please check: \n\n file: scenarios.xls" +
                      "\n sheet: " + scen_no + "\n\n")
    else:
        fltr_pols = scenario.loc[scenario['matrix'] == M_name]
        matrix = make_new(fltr_pols, M, M_name, labels)

    return (matrix)


def basic_mult(ide, a, kt, kp):
    """
    Policy intervention:
    It may be a primary intervention or an acillary action.

    a = a supply chain or a point in it subject to policy
    kt =  technical coefficient (max achievable technically)
    kp = penetration coefficient (level of market penet. of the policy)
    """
    if np.isnan(kt):
        return(a)
    elif np.isnan(kp):
        raise ValueError("please specify penetration coefficient for" +
                         " technical change -  Policy identifier "
                         + str(ide))
    else:
        kt = kt * 1e-2
        kp = kp * 1e-2
        totk = 1 - -kt * kp
        d = a * totk
        d = np.nan_to_num(d)
        return(d)


def basic_add(ide, a, at):
    """

    """
    if np.isnan(at):
        return(a)
    else:
        d = a + at
        d = np.nan_to_num(d)
        return(d)


def substitution(d, s, fx_kp):
    """
    Moves the value from one or multiple cells (in the same row or column)

    Substitution: Material subsitution or certain types of rebound effects

    If the size of the array of the original value is different from that
    of the destination (substituted), we obtain the total of the value to
    be substituted and the substitution is implemented by dividing the tot
    by the number of elements on the destination array and then added to
    the destination array (equally distributed)

    d = transaction with which we are substituting
    s = transaction that was subject to the direct policy intervention
    fx_kp = size of c that is added on the transaction to expand d
    """
    fx_kp = fx_kp * 1e-2
    if d.shape != s.shape:  # checking whether we need to distribute values
        s = np.sum(s.sum()) / (d.shape[0] * d.shape[1])
    else:
        pass

    ind = np.array(d) + (np.array(s) * fx_kp)
    ind = np.nan_to_num(ind)
    return(ind)


def copy(d, c, fx_kp):
    """
    Moves the value from one or multiple cells (in the same row or column)

    Substitution: Material subsitution or certain types of rebound effects

    d = transaction to expand
    c = transaction subject to the direct policy intervention
    fx_kp = size of c that is added on the transaction to expand d
    """
    fx_kp = fx_kp * 1e-2
    ind = np.array(d) + (np.array(c) * fx_kp)

    return(ind)


def counterfactual_engine(M, inter, subs=False, copy=False):
    """
    This function allows for the proccessing of the specified interventions
    onto a selected matrix. It calls various functions to modify the values
    in a specified matrix.

    M =  matrix of reference

    inter = contains all specs for the intervention

    y = index coordinate
    x = column coordinate
    ide = intervention identification number

    kt =  technical change coefficient
    kp = market penetration coefficient

    fx_kp = market penetration coeffient applicable to substitution

    expan = expansion coef. (used only for simple transaction changes)
    """

    ide = inter["ide"]

    y = inter["y"]
    print(y)
    x = inter["x"]
    a = M.iloc[y, x]

    if copy is True:
        y1 = inter["y1"]
        x1 = inter["x1"]
        d = M.iloc[y1, x1]
        if np.isnan(inter["swk"]):
            raise ValueError("I can't copy the values. You forgot to add" +
                             " the weighing factor for identifier no: " +
                             str(ide))
        else:
            M.iloc[y1, x1] = copy(d, a, inter["swk"])

    else:

        int1 = inter["kt1"]
        i1 = basic_mult(ide, a, int1["kt"], int1["kp"])

        int2 = inter["kt2"]
        i2 = basic_mult(ide, i1, int2["kt"], int1["kp"])

        int3 = inter["at1"]
        i3 = basic_add(ide, i2, int3["at"])

        int4 = inter["at2"]
        i4 = basic_add(ide, i3, int4["at"])

        M.iloc[y, x] = i4

        if subs is True:
            # Assumption is that subsitution can only happen if
            # a transaction is reduced
            y1 = inter["y1"]
            x1 = inter["x1"]

            sub = {"1": int1["sk"],
                   "2": int2["sk"],
                   "3": int3["sk"],
                   "4": int4["sk"]
                   }

            for key, value in sub.items():
                if value == "x":

                    if key == "1":
                        ref = a  # if it is the first sub then it will look
                    # at the difference b/ the original value and 1st inter
                    else:
                        key = int(key) - 1
                        ref = eval("i" + str(key))

                    s = ref - eval("i" + key)
                    d = M.iloc[y1, x1]
                    if np.isnan(inter["swk"]):
                        raise ValueError("I can't substitute the values." +
                                         "You forgot to add the weighing" +
                                         " factor for identifier no: " +
                                         str(ide))
                    else:
                        M.iloc[y1, x1] = substitution(d, s, inter["swk"])

    return(M)


def make_new(fltr_policies, M, M_name, labels):
    """
    Calculates and reassembles
    SUT or IOT matrices based on policy scenarios
    policy interventions

    scenario = is the table with the policy intervations

    M = matrix on which to implement the policies

    x = columns (abscissa/horizontal)
    y = rows (ordinate/vertical)

    *x.1 and *y.1  =  coordinates for destination in substitution
    """
    if labels.country_labels is None:
        reg_labels = labels.region_labels
    elif labels.country_labels is not None:
        reg_labels = labels.country_labels

    if "Y" in M_name:
        column_labels = labels.Y_labels
    elif M_name in ["A", "S", "L"]:
        column_labels = labels.cat_labels
        row_labels = labels.cat_labels
    else:
        name = [l for l in ["e", "m", "r", "w"] if l in M_name.lower()][0]
        attr_name = name.upper() + "_labels"
        row_labels = getattr(labels, attr_name)

    cat_labels = labels.cat_labels
    if len(fltr_policies) == 0:
        return (M)
    else:
        for l, row in fltr_policies.iterrows():

            inter = row.intervention
            ide = row.identifier  # used during debugging

            # Collecting the specified coordinates for the intevention

            # coordinates for region and category
            # Row items => Supplied category or extension category
            reg_o = positions.single_position(row.reg_o, reg_labels)
            cat_o = positions.single_position(row.cat_o, row_labels)

            # Column items => Consumption / manufacturing activity
            reg_d = positions.single_position(row.reg_o, reg_labels)
            cat_d = positions.single_position(row.cat_o, row_labels)

            # Translate coordinates from str to numerical position

            o_pos = positions(ind_M, reg_o, cat_o)
            d_pos = positions(col_M, reg_d, cat_d)

            # make dictionaries of all interventions
            kt1 = {"kt": row["kt1"], "kp": row["kp1"]}
            kt2 = {"kt": row["kt2"], "kp": row["kp2"]}

            at1 = {"at": row["at1"]}
            at2 = {"at": row["at2"]}

            # the following is only relevant for susbtitution
            if row["Sub"] == "x":

                ind_M1 = get_labels(M, 0)  # a matrix with all index labels
                col_M1 = get_labels(M, 1)  # matrix with all column labels

                reg_o1 = row["reg_o.1"]
                reg_d1 = row["reg_d.1"]

                cat_o1 = row["cat_o.1"]
                cat_d1 = row["cat_d.1"]

                o1_pos = positions(ind_M1, reg_o1, cat_o1)
                d1_pos = positions(col_M1, reg_d1, cat_d1)

                swk = row["swk"]  # Substitution weighing coefficient

                kt1["sk"] = row["sk1"]
                kt2["sk"] = row["sk2"]

                at1["sk"] = row["sk3"]
                at2["sk"] = row["sk4"]

                intervention = {"inter": inter,
                                "ide": ide,
                                "y": o_pos,
                                "x": d_pos,
                                "y1": o1_pos,
                                "x1": d1_pos,
                                "kt1": kt1,
                                "kt2": kt2,
                                "at1": at1,
                                "at2": at2,
                                "swk": swk
                                }

                substitution = True

            else:
                intervention = {"inter": inter,
                                "ide": ide,
                                "y": o_pos,
                                "x": d_pos,
                                "kt1": kt1,
                                "kt2": kt2,
                                "at1": at1,
                                "at2": at2
                                }

                substitution = False

            # direct copy of values to create proxies
            if row["Copy"] == "x":

                ind_M1 = get_labels(M, 0)  # a matrix with all index labels
                col_M1 = get_labels(M, 1)  # matrix with all column labels

                reg_o1 = row["reg_o.1"]
                reg_d1 = row["reg_d.1"]

                cat_o1 = row["cat_o.1"]
                cat_d1 = row["cat_d.1"]

                o1_pos = positions(ind_M1, reg_o1, cat_o1)
                d1_pos = positions(col_M1, reg_d1, cat_d1)

                swk = row["swk"]  # Substitution weighing coefficient

                intervention = {"inter": inter,
                                "ide": ide,
                                "y": o_pos,
                                "x": d_pos,
                                "y1": o1_pos,
                                "x1": d1_pos,
                                "kt1": "",
                                "kt2": "",
                                "at1": "",
                                "at2": "",
                                "swk": swk
                                }
                copy = True

            else:
                copy = False

#                print(ide, intervention)

            M = counterfactual_engine(M, intervention, substitution, copy)

    return(M)
