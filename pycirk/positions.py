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


def category_position(item, labels):
    """
    Takes a dataframe of the multiindex and identifies the position
    of the specified values    
    """
    
    if item in ["All","all","ALL", np.nan]:
        
        coordinate = None
        range_coordinates = None

    else:
        
        try:
            if item in labels.characterization:
                coordinate = [i for i, values in enumerate(labels.characterization) if item in values]
                range_coordinates = len(labels.characterization)
        except AttributeError:
            
            if item in labels.name:
                coordinate = [i for i, values in enumerate(labels.name) if item in values]
                range_coordinates = len(labels.names)
            elif item in labels.synonym:
                coordinate = [i for i, values in enumerate(labels.synonym) if item in values]
                range_coordinates = len(labels.synonym)
            elif item in labels.code:
                coordinate = [i for i, values in enumerate(labels.code) if item in values]
                range_coordinates = len(labels.code)
            elif item in labels.country_code:
                coordinate = [i for i, values in enumerate(labels.country_code) if item in values]
                range_coordinates = len(labels.country_code)
            elif item in labels.region:
                coordinate = [i for i, values in enumerate(labels.region) if item in values]
                range_coordinates = len(labels.region)
    
    set_of_coordinate = {"coordinate":coordinate, "range_coordinates":range_coordinates}
    
    return(set_of_coordinate)


def make_coord_array(coordinates, no_countries, no_categories):

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

    return(s)
