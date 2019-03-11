# -*- coding: utf-8 -*-
"""
Created on Wed Jan 23 10:58:46 2019

Description: Labelling elements for SUTs and IOTs

Scope: Modelling the Circular Economy in EEIO

@author:Franco Donati
@institution:Leiden University CML
"""

import numpy as np


def make_coord_array(coordinates, no_countries, no_ind_or_prod):

    n = 0
    nn = 0
    while n in range(len(coordinates)):
        while nn in range(no_countries):
            g = coordinates + no_ind_or_prod*nn
            if "s" not in locals():
                s = g
            else:
                s = np.concatenate([s, g])
            nn = nn+1
        n = n+1

    return(s)
