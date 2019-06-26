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

def make_counterfactuals_SUT(data, scen_no, scen_file, labels):

    met = ops.PxP_ITA_MSC

    w = ops.IOT.B(data.W, data.inv_diag_g)  # Primary input coef
    e = ops.IOT.B(data.E, data.inv_diag_g)  # emissions extension coef
    r = ops.IOT.B(data.R, data.inv_diag_g) # Resources extension coef
    m = ops.IOT.B(data.M, data.inv_diag_g) # Materials extension coef
    S = met.S(data.U, data.inv_diag_g)  # industry coefficients for intermediate use table

    # Start first from a supply approach
        # Supply matrix counterfactual
    data.V =  counterfactual(scen_file, scen_no, data.V, "V", labels)
        # new total industry output
    g_ = np.sum(data.V, axis=0)
        # industry use coefficients counterfactual
    S_ = counterfactual(scen_file, scen_no, S, "S", labels)
    data.U = counterfactual(scen_file, scen_no, S_ @ np.diag(g_), "U", labels)  # industry use transactions counterfactual
    W_ = np.array(ops.IOT.R(w, np.diag(g_)))
    _g_ = np.array(W_[:9].sum(0)) + data.U.sum(0)  # recalculate total industry output

    g_dif = np.multiply(_g_, ops.inv(data.g))  # calculate the difference between original and new total industry input

    print([round((1-l)*100,4) for l in g_dif if 1-l>.5e-3 and l!=0])
    data.Y = counterfactual(scen_file, scen_no, data.Y, "Y", labels)  # Final demand counterfactual

    q_ = np.sum(data.U, axis=1) + np.sum(data.Y, axis=1)

    # updating the supply table to match the new total industry input
    D = met.D(data.V, np.diag(ops.inv(data.V.sum(1))))
    data.V = D @ np.diag(q_)

    q1 = np.sum(data.V, axis=0)  # total product output

    q_dif = np.multiply(q_, ops.inv(q1))

    g1 = np.sum(data.V, axis=1)









    e = met.B(self.E, D, self.inv_diag_g)  # emis coef. matrix
    del(self.E)
    E = met.R(e, np.diag(x))

    r = met.B(self.R, D, self.inv_diag_g)  # resour coef. matrix
    del(self.R)
    R = met.R(r, np.diag(x))

    m = met.B(self.M, D, self.inv_diag_g)  # mater coef. matrix
    del(self.M)
    M = met.R(m, np.diag(x))

    x = ops.IOT.x_IAy(L, self.yi)  # total product ouput

    A = ops.IOT.A(Z, self.inv_diag_q)

    IOT = {"Y": data.Y,
           "L": L,
           "Z": Z,
           "A": A,
           "W": W,
           "E": E,
           "EY": data.EY,
           "R": R,
           "RY": data.RY,
           "M": M,
           "MY": data.MY,
           "Cr_E_k": data.Cr_E_k,
           "Cr_M_k": data.Cr_M_k,
           "Cr_R_k": data.Cr_R_k,
           "Cr_W_k": data.Cr_W_k,
           "ver_base": ver_base
           }

    return(IOT)



def make_counterfactuals(data, scen_no, scen_file, labels):
    """
    Calculate all the counterfactual IO matrices
    """
    # set basic data and variables

    data = deepcopy(data)

    x_ = ops.IOT.x(data.Z, data.Y)
    diag_x_ = np.diag(x_)
    inv_diag_x_ = ops.inv(diag_x_)

    diag_yj = np.diag(data.Y.sum(axis=0))
    inv_diag_yj = ops.inv(diag_yj)

    w = ops.IOT.B(data.W, inv_diag_x_)
    e = ops.IOT.B(data.E, inv_diag_x_)
    r = ops.IOT.B(data.R, inv_diag_x_)
    m = ops.IOT.B(data.M, inv_diag_x_)

    eY = ops.IOT.bY(data.EY, inv_diag_yj)
    rY = ops.IOT.bY(data.RY, inv_diag_yj)
    mY = ops.IOT.bY(data.MY, inv_diag_yj)

    data.Z = counterfactual(scen_file, scen_no, data.Z, "Z", labels)
    inv_diag_x_int = np.diag(ops.inv(ops.IOT.x(data.Z, data.Y)))

    A = ops.IOT.A(data.Z, inv_diag_x_int)
    data.A = counterfactual(scen_file, scen_no, A, "A", labels)

    data.Y = counterfactual(scen_file, scen_no, data.Y, "Y", labels)

    L = ops.IOT.L(data.A)

    x_new = ops.IOT.x_IAy(L, data.Y.sum(1))
    diag_x_new = np.diag(x_new)

    diag_yj_new = np.diag(data.Y.sum(axis=0))

    # Apply policy to economic matrices

    # Apply policy to intermediate extension intensities
    data.w = counterfactual(scen_file, scen_no, w, "w", labels)
    data.e = counterfactual(scen_file, scen_no, e, "e", labels)
    data.r = counterfactual(scen_file, scen_no, r, "r", labels)
    data.m = counterfactual(scen_file, scen_no, m, "m", labels)

    # Apply policy to final demand extension intensities

    data.eY = counterfactual(scen_file, scen_no, eY, "eY", labels)
    data.rY = counterfactual(scen_file, scen_no, rY, "rY", labels)
    data.mY = counterfactual(scen_file, scen_no, mY, "mY", labels)

    data.Z = ops.IOT.Z(data.A, diag_x_new)

    data.W = ops.IOT.R(data.w, diag_x_new)  # primary inputs coef

    data.E = ops.IOT.R(data.e, diag_x_new)  # emissions ext coef

    data.R = ops.IOT.R(data.r, diag_x_new)  # resource ext coef
    data.M = ops.IOT.R(data.m, diag_x_new)  # material ext coef

    data.EY = ops.IOT.RY(data.eY, diag_yj_new)  # emissions ext FD coef
    data.RY = ops.IOT.RY(data.rY, diag_yj_new)  # resource ext FD coef
    data.MY = ops.IOT.RY(data.mY, diag_yj_new)  # material ext FD coef

    data.W = counterfactual(scen_file, scen_no, data.W, "W", labels)

    # Apply policy to intermediate extension coefficient matrices
    data.E = counterfactual(scen_file, scen_no, data.E, "E", labels)
    data.R = counterfactual(scen_file, scen_no, data.R, "R", labels)
    data.M = counterfactual(scen_file, scen_no, data.M, "M", labels)

    # Apply policy to  final demand extension coefficient matrices
    data.EY = counterfactual(scen_file, scen_no, data.EY, "EY", labels)
    data.RY = counterfactual(scen_file, scen_no, data.RY, "RY", labels)
    data.MY = counterfactual(scen_file, scen_no, data.MY, "MY", labels)

    print((1-np.sum(x_)/np.sum(x_new))*100)

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


    scenario = pd.read_excel(scen_file, sheet_name=scen_no, header=1, index=None)

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
    g = inter_sets["g"]  # columns

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

    spec_labels = labels.identify_labels(M_name)

    reg_labels = spec_labels["reg_labels"]
    row_labels = spec_labels["i_labels"]
    column_labels = spec_labels["g_labels"]
    no_row_labs = spec_labels["no_i"]
    no_col_labs = spec_labels["no_g"]
    no_reg_labs = spec_labels["no_reg"]

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
