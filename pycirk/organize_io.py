# -*- coding: utf-8 -*-
"""
Created on Tue Feb 7 16:29:23 2017

Description: Organize essential tables for saving

Scope: Modelling the Circular economy in EEIO


@author: Franco Donati
@institution: Leiden University CML
"""

import numpy as np

def organizer(data):

    return {"Z": np.array(data["Z"]),
            "Y": np.array(data["Y"]),
            "W": np.array(data["W"]),
            "E": np.array(data["E"]),
            "R": np.array(data["R"]),
            "M": np.array(data["M"]),
            "EY": np.array(data["EY"]),
            "RY": np.array(data["RY"]),
            "MY": np.array(data["MY"]),
            "Cr_E_k": np.array(data["Cr_E_k"]),
            "Cr_M_k": np.array(data["Cr_M_k"]),
            "Cr_R_k": np.array(data["Cr_R_k"]),
            "Cr_W_k": np.array(data["Cr_W_k"])
            }