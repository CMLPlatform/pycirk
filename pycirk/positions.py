# -*- coding: utf-8 -*-
"""
Created on Wed Jan 23 10:58:46 2019

Description: Finding the position of labels

Scope: Modelling the Circular Economy in EEIO

@author:Franco Donati
@institution:Leiden University CML
"""

import numpy as np


def single_position(item, labels):
    """
    Takes a dataframe of the multiindex and identifies the position
    of the specified values

    Parameters
    ----------

    item : str
        The label the user is looking for

    labels : obj
        An object cointaining a set of labels
        (as specified in the labels.py module)

    Output
    ------
    An numpy.array containing the coordinate of a specific label
    or None in case of there is no specified label

    """

    if item in ["All", "all", "ALL", np.nan]:
        return None

    else:
        try:
            if item in labels:
                ref_labels = labels.copy()
        except Exception:
            pass

        try:
            if item in labels.name:
                ref_labels = labels.name.copy()
            elif item in labels.synonym:
                ref_labels = labels.synonym.copy()
            elif item in labels.code:
                ref_labels = labels.code.copy()
        except Exception:
            pass

        try:
            if item in labels.characterization:
                ref_labels = labels.characterization.copy()
        except Exception:
            pass
        
        return np.array([i for i, values in enumerate(ref_labels)
                              if item in values])

def make_coord_array(cat_coord, reg_coord, no_countries, no_categories):
    """
    It creates an an array of coordinates based on the specification of the
    users.

    Parameters
    ----------
    cat_coord : int, numpy.array, bool
        the numerical coordinate of a specific category belonging to a matrix
        in the IO or SUT system. If None is passed then it will return an
        array of all coordinates in range no_categories.

    reg_coord : int, numpy.array, bool
        the numerical coordinate of a specific region in the IO or SUT system.
        If None is passed then it will return an array of all coordinates in
        range no_countries.

    no_countries : int
        the total number of countries or regions in the dataset

    no_categories : int
        the total number of categories referring one axis in the chosen matrix

    Output
    ------
    A numpy.array referring to each coordinate point specified by the user
    """

    if no_categories not in [7, 163, 200]:
        no_countries = 1
    else:
        pass
    
    if cat_coord is None:
        s = np.array(range(no_categories * no_countries))
    else:
        n = 0
        while n in range(no_countries):

            g = cat_coord[0] + no_categories * n
            if "s" not in locals():
                s = np.array([g])
            else:
                s = np.append(s, g)
            n = n+1
    
    if reg_coord is None:
        return s
    else:
        s = np.split(s, no_countries)    
        s = s[reg_coord[0]]
        return s

def make_coord_array_for_make_sec(coordinates, no_countries, no_categories):
    """
    It creates an an array of coordinates based on the total location
    of secondary materials and processing categories

    Parameters
    ----------
    coordinates : int, numpy.array
        the numerical coordinate of secondary categories belonging to the SUT system

    no_countries : int
        the total number of countries or regions in the dataset

    no_categories : int
        the total number of categories referring one axis in the chosen matrix

    Output
    ------
    A numpy.array referring to each coordinate point
    """

    n = 0
    nn = 0
    while n in range(len(coordinates)):
        while nn in range(no_countries):
            g = coordinates + no_categories * nn
            if "s" not in locals():
                s = g
            else:
                s = np.concatenate([s, g])
            nn = nn+1
        n = n+1

    return s
