# -*- coding: utf-8 -*-
"""
Created on Tue Feb 7 16:29:23 2017

Description: Calculate baseline and scenarios in IOT

Scope: Modelling the Circular economy in EEIO


@author: Franco Donati
@institution: Leiden University CML
"""


def organizer(data):

    IOT = {"S": data["S"],
           "Y": data["Y"],
           "W": data["W"],
           "E": data["E"],
           "R": data["R"],
           "M": data["M"],
           "YE": data["YE"],
           "YR": data["YR"],
           "YM": data["YM"],
           "Cr_E_k": data["Cr_E_k"],
           "Cr_M_k": data["Cr_M_k"],
           "Cr_R_k": data["Cr_R_k"],
           "Cr_W_k": data["Cr_W_k"]
           }

    return(IOT)
