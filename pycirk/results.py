# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 09:26:43 2017

Description: module to perform results analysis

Scope: Modelling the Circular Economy in EEIO

@author:Franco Donati
@institution:Leiden University CML, TU Delft TPM
"""
import warnings
import pandas as pd
from pandas import DataFrame as df
from pandas import MultiIndex as mi
import numpy as np
from pycirk.positions import make_coord_array as coord
from pycirk.positions import single_position as sing_pos
from pycirk.fundamental_operations import Operations as ops
warnings.simplefilter(action='ignore', category=FutureWarning)


def iter_thru_for_results(data, analysis_specs, scen_no, labels):
    """
    It uses your analytical specification on scenarios.xlxl
    to return a dataframe of the desired results
    """
    results = []

    for l, v in analysis_specs.iterrows():
        res = retrieve_specified_data(data, v, labels)
        if len(results) == 0:
            results = res
        else:
            results = pd.concat([results, res], axis=0)

    if scen_no not in [0, "baseline", "base", None]:
        results.columns = ["sc_" + str(scen_no)]
    else:
        results.columns = ["baseline"]
    
    return results

def rsd_engine(data, M_name, spec_row, labels):
        
    
    M = np.array(data[M_name])  # Call specific matrix from which to select
    
    spec_labels = labels.identify_labels(M_name)
    
    reg_labels = spec_labels["reg_labels"]
    row_labels = spec_labels["i_labels"]
    column_labels = spec_labels["g_labels"]
    no_row_labs = spec_labels["no_i"]
    no_col_labs = spec_labels["no_g"]
    no_reg_labs = spec_labels["no_reg"]

    i_cat = spec_row.o_p  # rows
    i_reg = spec_row.o_r

    g_cat = spec_row.d_p  # columns
    g_reg = spec_row.d_r

    try:
        cat_o = sing_pos(i_cat, row_labels)
        reg_o = sing_pos(i_reg, reg_labels)
        # Column items (g) => Consumption / manufacturing activity
        cat_d = sing_pos(g_cat, column_labels)
        reg_d = sing_pos(g_reg, reg_labels)

        # Identify coordinates
        i = coord(cat_o, reg_o, no_reg_labs, no_row_labs)

        g = coord(cat_d, reg_d, no_reg_labs, no_col_labs)
    except UnboundLocalError:
        raise ValueError(f"\nThe specified coordinates to retrieve results are wrong.\nPlease check that name and matrix in your scenarios.xlsx file are correct.\nCheck: {M_name, i_cat}")



    select = df([M[np.ix_(i, g)].sum()])


    key_names = ["matrix", "i_category", "i_region", "g_category",
                 "g_region", "unit"] 
        

    try:
        unit = str(row_labels.unit[cat_o].iloc[0])
    except Exception:
        unit = str(row_labels.unit[0])

    index_label = [M_name, i_cat, i_reg, g_cat, g_reg, unit]

    select.index = mi.from_tuples([index_label], names=key_names)
    
    return select

def retrieve_specified_data(data, spec_row, labels):
    """
    Separate, collect and rename results for base and scenarios according
    to specifications under th sheet "analysis" in scenarios.xls

    data = any IOT table
    spec_row = row in the scenarios sheet specifying settings
    """

    pd.options.display.float_format = '{:,.4f}'.format

    M_name = spec_row.matrix  # matrix of reference
    
    if "Cr" in M_name:
            data = ops.calculate_characterized(data)

    if "tot" in M_name:
        M_name_1 = M_name[-1]
        M_name_2 = M_name[-1] + "Y"
        
        if "Cr" in M_name:
            M_name_1 = "Cr_" + M_name_1
            M_name_2 = "Cr_" + M_name_2                
                
                
        output = rsd_engine(data, M_name_1, spec_row, labels)
        output = output + rsd_engine(data, M_name_2, spec_row, labels).values
        index_label = [list(i) for i in output.index][0]
        index_label[0] = M_name
        key_names = output.index.names
        output.index = mi.from_tuples([index_label], names=key_names)
    else:
        output = rsd_engine(data, M_name, spec_row, labels)
                       
    return output
            
            


