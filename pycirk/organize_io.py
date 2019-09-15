# -*- coding: utf-8 -*-
"""
Created on Tue Feb 7 16:29:23 2017

Description: Organize essential tables for saving

Scope: Modelling the Circular economy in EEIO


@author: Franco Donati
@institution: Leiden University CML
"""


def organizer(data):

    return {"Z": data["Z"],
            "Y": data["Y"],
            "W": data["W"],
            "E": data["E"],
            "R": data["R"],
            "M": data["M"],
            "EY": data["EY"],
            "RY": data["RY"],
            "MY": data["MY"],
            "Cr_E_k": data["Cr_E_k"],
            "Cr_M_k": data["Cr_M_k"],
            "Cr_R_k": data["Cr_R_k"],
            "Cr_W_k": data["Cr_W_k"]
            }