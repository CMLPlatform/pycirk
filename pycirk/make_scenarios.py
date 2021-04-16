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


def make_counterfactuals(data, scen_no, scen_file, labels):
    """
    Calculate all the counterfactual IO matrices

    Parameters
    ----------
    data : obj
        An object containing all necessary matrices of the IO system

    scen_no : int
        the identification number of the scenario to reference in scen_file

    scen_file : str
        the directory where the scenarios.xlsx file is store

    labels : obj
        an object containing all labels for the IO matrices

    Outputs
    -------
    An object contaning a mofified IO system
    """
    # set basic data and variables
    print(f"Scenario {scen_no} started")
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

    # Apply policy to economic matrices
    data.Z = counterfactual(scen_file, scen_no, data.Z, "Z", labels)
    inv_diag_x_int = np.diag(ops.inv(ops.IOT.x(data.Z, data.Y)))

    A = ops.IOT.A(data.Z, inv_diag_x_int)

    data.A = counterfactual(scen_file, scen_no, A, "A", labels)

    data.Y = counterfactual(scen_file, scen_no, data.Y, "Y", labels)

    L = ops.IOT.L(data.A)

    x_new = ops.IOT.x_IAy(L, data.Y.sum(1))
    
    diag_x_new = np.diag(x_new)

    diag_yj_new = np.diag(data.Y.sum(axis=0))

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

    #print((1-np.sum(x_)/np.sum(x_new))*100)
    print(f"Scenario {scen_no} completed")

    return data


def counterfactual(scen_file, scen_no, M, M_name, labels):
    """
    Separates changes by matrix subject to intervention and apply them on a
    specific matrix

    Parameters
    ----------
        scen_file: str
            directory of the file in which the scenarios are specified
        scen_no : int
            specific scenario e.g "1" or "scenario_1"
        M : numpy.array
            matrix affected by the policies
        M_name : str
            matrix name as diplayed under sheet_name["matrix"]
        labels : obj
            matrix labels
    Output
    ------
    A numpy array modified according to the specified changes in the scenario file

    """

    if type(scen_no) is int:
        scen_no = "scenario_" + str(scen_no)

    elif scen_no.startswith("scenario_"):
        pass
    else:
        raise KeyError("only integer or explicit name (scenario_x) are allowed")


    scenario = pd.read_excel(scen_file, sheet_name=scen_no, header=1)

    if scenario["matrix"].isnull().values.all():
        matrix = M
        warnings.warn("\n\nA scenario sheet was found but no parameters" +
                      "were set, please check: \n\n file: scenarios.xls" +
                      "\n sheet: " + scen_no + "\n\n")
    else:
        filtered_changes = scenario.loc[scenario['matrix'] == M_name]
        matrix = make_new(filtered_changes, M, M_name, labels)

    return matrix


def basic_mult(ide, a, kt, kp):
    """
    Policy intervention

    It may be a primary intervention or an acillary action.

    Parameters
    ----------
    a: numpy.array
        a supply chain or a point in it subject to a change

    kt: float
        technical coefficient (max achievable technically)

    kp: float
        penetration coefficient (level of market penet. of the policy)

    ide: int
       identification number of the intervention in case of missing information

    Output
    ------
    A a numpy.array of the same order/shape of a

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

    return d


def basic_add(a, at):
    """
    Adds values together

    Parameters
    ----------

    a : numpy.array

    at :  numpy array
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

    Parameters
    ----------
    d : numpy.array
        transaction with which we are substituting

    s : numpy.array
        original transaction that was subject to changes
        (the transactions from which the value is coming from)

    fx_kp : float
        relative size of c that is added on the transaction to expand d

    Output
    ------
    A numpy.array of modified d
    """
    fx_kp = fx_kp * 1e-2
    if d.shape != s.shape:  # checking whether we need to distribute values

        mask = (d == 0)
        no_non_zeros = np.count_nonzero(d)
        d[~mask] = d[~mask] + (np.sum(s.sum())/no_non_zeros) * fx_kp
    else:
        d = d + np.array(s) * fx_kp
    return d



def counterfactual_engine(M, inter_sets, subs=False, copy=False):
    """
    This function allows for the proccessing of the specified interventions
    onto a selected matrix. It calls various functions to modify the values
    in a specified matrix.

    Parameters
    ----------

    M : numpy.array
        matrix of reference

    inter_sets: dict
        contains all specfication concerning the changes to be applied
        (intervention sets)

    subs : bool
        If True it will call the subsitution function according to
        specifications in scenarios.xlsx

    copy : bool
        if True it will copy value from one part of the matrix to another
        according to specifications in scenarios.xlsx

    Others
    -------
    i : index coordinate

    g : column coordinate

    ide : intervention identification number

    kt :  technical change coefficient

    kp : market penetration coefficient

    fx_kp : market penetration coeffient applicable to substitution

    expan : expansion coef. (used only for simple transaction changes)

    Output
    ------
    A numpy.array of the modified matrix

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
            raise ValueError(f"I can't copy the values. You forgot to add the weighing factor for identifier no: {ide}")
        else:
            M[np.ix_(i1, g1)] = d + (a * inter_sets["swk"]*1e-2)

    else:

        int1 = inter_sets["kt1"]
        int1 = basic_mult(ide, a, int1["kt"], int1["kp"])

        int2 = inter_sets["kt2"]
        int2 = basic_mult(ide, int1, int2["kt"], int2["kp"])

        int3 = inter_sets["at1"]
        int3 = basic_add(int2, int3)

        int4 = inter_sets["at2"]
        int4 = basic_add(int3, int4)
        M[np.ix_(i, g)] = int4

        if subs is True:
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
                    if np.isnan(inter_sets["swk"]):
                        raise ValueError(f"I can't substitute the values. You forgot to add the weighing factor for identifier no: {ide}")
                    else:
                        hey = substitution(d, s, inter_sets["swk"])
                        M[np.ix_(i1, g1)] = hey

    return M


def make_new(filtered_changes, M, M_name, labels):
    """
    Organizes the data concerning the changes and calls the functions
    to modified matrices based on specied scenarios

    Parameters
    ----------
    filterd_changes: pandas.DataFrame
        A table filtered by matrix name containing all changes to be applied

    M : numpy.array
        matrix on which to implement the changes

    M_name : str
        nomenclature referring to the matrix to be changed

    labels: obj
        object containing all matrix labels

    Others
    ------
    g is any column in the matrix

    i is any row row in the matrix

    Output
    ------
    A numpy.array of the processed matrix

    """

    M = np.array(M)

    spec_labels = labels.identify_labels(M_name)

    reg_labels = spec_labels["reg_labels"]
    row_labels = spec_labels["i_labels"]
    column_labels = spec_labels["g_labels"]
    no_row_labs = spec_labels["no_i"]
    no_col_labs = spec_labels["no_g"]
    no_reg_labs = spec_labels["no_reg"]

    if len(filtered_changes) == 0:
        return (M)
    else:
        for l, entry in filtered_changes.iterrows():
            try:
                change_type = entry.change_type
                ide = entry.identifier  # used during debugging
    
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
                #print(f"row\n ide: {ide}, row: {entry.reg_o}, {entry.cat_o}, {orig_coor}")
                dest_coor = coord(cat_d, reg_d, no_reg_labs, no_col_labs)
                #print(f"columns\n ide: {ide}, column: {entry.reg_d}, {entry.cat_d}, {dest_coor}")
                
                # organize main changes
                kt1 = {"kt": entry.kt1, "kp": entry.kp1}
                kt2 = {"kt": entry.kt2, "kp": entry.kp2}
    
                intervention = {"change_type": change_type,
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
            except Exception:
                raise ValueError(f"Check in this entry for potential coordinate errors in your scenario settings:\n{entry} ")

            M = counterfactual_engine(M, intervention, substitution, copy)
    
    return M
