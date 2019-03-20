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
from pycirk.labels import positions
from pycirk.SUTops import sops
from pycirk.labels import get_labels
from pandas import DataFrame as df
import warnings

def sceneIOT(data, scen_no, scen_file):
    """
    baseline IOT calculated with Technical Coefficient or
    Market coefficient method
    """
    data = data.copy()
    
    # Apply policy to economic matrices
    data.S = apply_policy(scen_file, scen_no, data.S, "S")
    inv_diag_x = sops.inv(np.diag(sops.IOT.x(data.S, data.Y)))
    A = sops.IOT.A(data.S, inv_diag_x)
    data.A = apply_policy(scen_file, scen_no, df(A), "A")

    data.Y = apply_policy(scen_file, scen_no, data.Y, "Y")
    data.RE = apply_policy(scen_file, scen_no, data.RE, "RE")

    # Apply policy to intermediate extension coefficient matrices
    data.RBe = apply_policy(scen_file, scen_no, data.RBe, "RBe")
    data.RBr = apply_policy(scen_file, scen_no, data.RBr, "RBr")
    data.RBm = apply_policy(scen_file, scen_no, data.RBm, "RBm")

    # Apply policy to  final demand extension coefficient matrices
    data.RYBe = apply_policy(scen_file, scen_no, data.RYBe, "RYBe")
    data.RYBr = apply_policy(scen_file, scen_no, data.RYBr, "RYBr")
    data.RYBm = apply_policy(scen_file, scen_no, data.RYBm, "RYBm")

    # Scenario
    data.L = sops.IOT.L(data.A)  # L from S and Y modified

    yi = np.sum(data.Y, axis=1)  # row sum of final demand
    diag_yj = np.diag(data.Y.sum(axis=0))  # column sum of FD
    data.x = sops.IOT.x_IAy(data.L, yi)
    diag_x = np.diag(data.x)

    data.S = sops.IOT.S(data.A, diag_x)

    data.E = sops.IOT.B(data.RE, diag_x)  # primary inputs

    data.Be = sops.IOT.B(data.RBe, diag_x)  # emissions ext
    data.Br = sops.IOT.B(data.RBr, diag_x)  # resource ext
    data.Bm = sops.IOT.B(data.RBm, diag_x)  # material ext

    data.YBe = sops.IOT.FD_EXT(data.RYBe, diag_yj)  # emissions ext
    data.YBr = sops.IOT.FD_EXT(data.RYBr, diag_yj)  # resource ext
    data.YBm = sops.IOT.FD_EXT(data.RYBm, diag_yj)  # material ext

    # Characterisation
    data.CrBe = np.matmul(data.CrBe, data.Be)  # emissions ext
    data.CrBr = np.matmul(data.CrBr, data.Br)  # resource ext
    data.CrBm = np.matmul(data.CrBm, data.Bm)  # material ext
    data.CrE = np.matmul(data.CrE, data.E)  # factor inputs

    data.CrYBe = np.matmul(data.CrBe, data.YBe)  # emissions ext
    data.CrYBr = np.matmul(data.CrBr, data.YBr)  # resource ext
    data.CrYBm = np.matmul(data.CrBm, data.YBm)  # material ext

    data.ver = sops.verifyIOT(data.S, data.Y, data.E)  # ver_new_IOT

    return(data)

def apply_policy(scen_file, scen_no, M, M_name):
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
        matrix = make_new(fltr_pols, M, M_name)

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


def policy_engine(M, inter, subs=False, copy=False):
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

#        name = inter["inter"]
    ide = inter["ide"]

    y = inter["y"]
    x = inter["x"]
    a = M.iloc[y, x]
#        test = [M.iloc[y,x]]
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


def make_new(fltr_policies, M, M_name):
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

    if len(fltr_policies) == 0:
        return (M)
    else:
        for l, row in fltr_policies.iterrows():

            inter = row["intervention"]
            ide = row["identifier"]  # used during debugging

            # Collecting the specified coordinates for the intevention

            # coordinates for region and category
            reg_o = row["reg_o"]
            reg_d = row["reg_d"]

            cat_o = row["cat_o"]
            cat_d = row["cat_d"]
            
            # Translate coordinates from str to numerical position
            
            # get the labels from the matrix
            ind_M = get_labels(M, 0)  # a matrix with all index labels
            col_M = get_labels(M, 1)  # matrix with all column labels

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

            M = policy_engine(M, intervention, substitution, copy)

    return(M)
