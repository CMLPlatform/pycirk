# -*- coding: utf-8 -*-
"""
Created on Wed Jan 23 10:58:46 2019

Description: Finding the position of labels

Scope: Modelling the Circular Economy in EEIO

@author:Franco Donati
@institution:Leiden University CML
"""

import numpy as np

# Started doing some generalization work, but still in the process
# I don't know whether it's worth the effort.
# Maybe somebody else will want to give a crack at it


def positions(ind_df, reg, cat):
    """
    Takes a dataframe of the multiindex and identifies the position
    of the specified values
    reg = regions [EU or ROW]
    cat = category of synonym [C_STEL]
    """

#    if reg in ["EU", "ROW"]:
#        no_reg = 2
#        no_cat = len(ind_df)/no_reg
#        if no_cat not in [163, 200]:
#            no_cat = input("Specify number of product/sector categories in" +
#                           "your database:\n")
#    elif len(ind_df)/49 in [163, 200]:
#        no_reg = 49
#        no_cat = len(ind_df)/no_reg
#    else:
#        no_cat = input("Specify no of products/sectors in your database:\n")
#        no_reg = input("Specify no of regions in your database:\n")
#
#    ind_df = ind_df.iloc[:len(ind_df)/no_reg]

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


# def make_coord_array(coordinates, no_countries, no_ind_or_prod):
#
#    n = 0
#    nn = 0
#    while n in range(len(coordinates)):
#        while nn in range(no_countries):
#            g = coordinates + no_ind_or_prod*nn
#            if "s" not in locals():
#                s = g
#            else:
#                s = np.concatenate([s, g])
#            nn = nn+1
#        n = n+1
#
#    return(s)
