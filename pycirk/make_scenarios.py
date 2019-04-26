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
from pycirk.positions import make_coord_array as coord
from pycirk.positions import single_position as sing_pos
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
    data.Z = counterfactual(scen_file, scen_no, data.Z, "Z", labels)

    # First total product output from changes in S
    x_ = ops.IOT.x(data.Z, data.Y)
    diag_x_ = np.diag(x_)
    inv_diag_x_ = ops.inv(diag_x_)

    A = ops.IOT.A(data.Z, inv_diag_x_)

    diag_yj = np.diag(data.Y.sum(axis=0))

    data.A = counterfactual(scen_file, scen_no, A, "A", labels)
    data.Y = counterfactual(scen_file, scen_no, data.Y, "Y", labels)

    x = ops.IOT.x(data.Z, data.Y)
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

    data.Z = ops.IOT.Z(data.A, diag_x)

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
        d = a
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
        at = 0

    a += at

    return(a)


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
        print(d.shape, s.shape)
        print(d)
        d = (d.shape[0] * d.shape[1])
        mask = (d == 0)
        d[~mask] = 1/d[~mask]
        s = np.sum(s.sum()) * d
    else:
        pass

    ind = np.array(d) + (np.array(s) * fx_kp)
    ind = np.nan_to_num(ind)
    return(ind)


def counterfactual_engine(M, inter_sets, subs=False, copy=False):
    """
    This function allows for the proccessing of the specified interventions
    onto a selected matrix. It calls various functions to modify the values
    in a specified matrix.

    M =  matrix of reference

    inter = contains all specs for the intervention

    i = index coordinate
    g = column coordinate
    ide = intervention identification number

    kt =  technical change coefficient
    kp = market penetration coefficient

    fx_kp = market penetration coeffient applicable to substitution

    expan = expansion coef. (used only for simple transaction changes)
    """

    ide = inter_sets["ide"]

    i = inter_sets["i"]  # row
    print("i",i)
    g = inter_sets["g"]  # columns
    print("g",g)

    a = M[np.ix_(i, g)]

    if copy is True:
        i1 = inter_sets["i1"]
        g1 = inter_sets["g1"]
        d = M[np.ix_(i1, g1)]
        if np.isnan(inter_sets["swk"]):
            raise ValueError("I can't copy the values. You forgot to add" +
                             " the weighing factor for identifier no: " +
                             str(ide))
        else:
            print("d", d)
            print("a", a)
            print("swk", type(inter_sets["swk"]))
            print("i1", i1, "g1", g1)
            M[np.ix_(i1, g1)] = d + (a * inter_sets["swk"]*1e-2)

    else:

        int1 = inter_sets["kt1"]
        int1 = basic_mult(ide, a, int1["kt"], int1["kp"])

        int2 = inter_sets["kt2"]
        int2 = basic_mult(ide, int1, int2["kt"], int2["kp"])

        int3 = inter_sets["at1"]
        int3 = basic_add(ide, int2, int3)

        int4 = inter_sets["at2"]
        int4 = basic_add(ide, int3, int4)

        M[np.ix_(i, g)] = int4

        if subs is True:
            # Assumption is that subsitution can only happen if
            # a transaction is reduced
            i1 = inter_sets["i1"]
            g1 = inter_sets["g1"]

            sub = {"1": inter_sets["sk1"],
                   "2": inter_sets["sk2"],
                   "3": inter_sets["sk3"],
                   "4": inter_sets["sk4"]
                   }

            for key, value in sub.items():
                if value == "x":

                    if key == "1":
                        ref = a  # if it is the first sub then it will look
                    # at the difference b/ the original value and 1st inter
                    else:
                        print("and here")
                        key = int(key) - 1
                        ref = eval("int" + str(key))

                    s = ref - eval("int" + str(key))
                    d = M[np.ix_(i1, g1)]
#                    print(i1, g1)
                    if np.isnan(inter_sets["swk"]):
                        raise ValueError("I can't substitute the values." +
                                         "You forgot to add the weighing" +
                                         " factor for identifier no: " +
                                         str(ide))
                    else:
                        M[np.ix_(i1, g1)] = substitution(d, s, inter_sets["swk"])

    return(M)


def make_new(fltr_policies, M, M_name, labels):
    """
    Calculates and reassembles
    SUT or IOT matrices based on policy scenarios
    policy interventions

    scenario = is the table with the policy intervations

    M = matrix on which to implement the policies

    g = columns (abscissa/horizontal)
    i = rows (ordinate/vertical)

    """

    M = np.array(M)

    # identifying colum and index labels
    if labels.country_labels is None:
        reg_labels = labels.region_labels
    elif labels.country_labels is not None:
        reg_labels = labels.country_labels

    if "Y" in M_name:
        column_labels = labels.Y_labels
        row_labels = labels.cat_labels
    else:
        column_labels = labels.cat_labels
        row_labels = labels.cat_labels

    if M_name.lower()[0] in ["e", "m", "r", "w"]:
        name = [l for l in ["e", "m", "r", "w"] if l in M_name.lower()][0]
        attr_name = name.upper() + "_labels"
        row_labels = getattr(labels, attr_name)

    no_row_labs = row_labels.count
    no_reg_labs = len(reg_labels)
    no_col_labs = column_labels.count

    if len(fltr_policies) == 0:
        return (M)
    else:
        for l, entry in fltr_policies.iterrows():

            inter = entry.intervention
            ide = int(entry.identifier)  # used during debugging

            # Collecting the specified coordinates for the intevention

            # coordinates for region and category
            # Row items (i) => Supplied category or extension category
            reg_o = sing_pos(entry.reg_o, reg_labels)
            cat_o = sing_pos(entry.cat_o, row_labels)

            # Column items (g) => Consumption / manufacturing activity
            reg_d = sing_pos(entry.reg_d, reg_labels)
            cat_d = sing_pos(entry.cat_d, column_labels)

            # Identify coordinates
            orig_coor = coord(cat_o, reg_o, no_reg_labs, no_row_labs)
            dest_coor = coord(cat_d, reg_d, no_reg_labs, no_col_labs)

            # organize main changes
            kt1 = {"kt": entry.kt1, "kp": entry.kp1}
            kt2 = {"kt": entry.kt2, "kp": entry.kp2}

            intervention = {"inter": inter,
                            "ide": ide,
                            "i": orig_coor,
                            "g": dest_coor,
                            "kt1": kt1,
                            "kt2": kt2,
                            "at1": entry.at1,
                            "at2": entry.at2,
                            }

            substitution = False
            copy = False

            # the following is only relevant for susbtitution
            if "x" in [entry.Sub, entry.Copy]:

                sub_reg_o = sing_pos(entry.reg_o_sc, reg_labels)
                sub_cat_o = sing_pos(entry.cat_o_sc, row_labels)

                # Column items => Consumption / manufacturing activity
                sub_reg_d = sing_pos(entry.reg_d_sc, reg_labels)
                sub_cat_d = sing_pos(entry.cat_d_sc, column_labels)

                # Translate coordinates from str to numerical position
                sub_orig_coor = coord(sub_cat_o, sub_reg_o, no_reg_labs, no_row_labs)
                sub_dest_coor = coord(sub_cat_d, sub_reg_d, no_reg_labs, no_col_labs)

                intervention["swk"] = entry.swk
                intervention["i1"] = sub_orig_coor
                intervention["g1"] = sub_dest_coor
                intervention["sk1"] = entry.sk1
                intervention["sk2"] = entry.sk2
                intervention["sk3"] = entry.sk3
                intervention["sk4"] = entry.sk4

                if entry.Copy == "x":
                    copy = True
                elif entry.Sub == "x":
                    substitution = True


            M = counterfactual_engine(M, intervention, substitution, copy)

    return(M)
