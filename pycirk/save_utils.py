# -*- coding: utf-8 -*-
"""
Created on Sat Mar  4 11:02:52 2017

Description: Save data to xls

Scope: Modelling circular economy policies in EEIOA


@author: Franco Donati
@institution: Leiden University CML
"""
import os
import datetime
import pandas as pd
import pickle as pk
from shutil import copyfile
from pandas import DataFrame as df
from openpyxl import load_workbook
now = datetime.datetime.now()

def save_outputs(results, directory, specs, scen_no, data=None):
    """
    It saves results into a previously specified directory
    """
    date = "_".join([str(now.year), str(now.month), str(now.day)])
    time = "_".join([str(now.hour), str(now.minute)])
    directory_or = directory
    directory_out = os.path.join(directory, "output_" + date)
    print(directory_out)

    if scen_no in ["baseline", 0, "base"]:
        scen_no = "baseline"
        path = os.path.join(directory_out, "baseline", time)
    elif scen_no > 0:
        scen_no = "scenario_" + str(scen_no)
        specs["scenario_number"] = scen_no
        path = os.path.join(directory_out, "_".join([str(scen_no)]), time)

    if not os.path.exists(path):
        os.makedirs(path)

    specs = add_date_to_gen_specs(specs)

    copyfile(directory_or + "scenarios.xlsx", os.path.join(path, "results_and_settings.xlsx"))

    with pd.ExcelWriter(path + "/" + "results_and_settings.xlsx", engine="openpyxl") as writer:
        writer.book = load_workbook(path + "/" +"results_and_settings.xlsx")
        specs.to_excel(writer, sheet_name="General", startrow=1, startcol=1)
        results.to_excel(writer, "Results", startrow=1, startcol=1, merge=False)
        writer


    if data is not None:
        w = open(path + "/"+ "data.pkl", "wb")
        pk.dump(data, w, 2)

        w.close()

def add_date_to_gen_specs(specs):
    """
    Assembles general specifications e.g. authors, institution etc
    """
    year, month, day = str(now.date()).split("-")

    timemark = "/".join([day, month, year])

    specs["timemark"] = timemark

    #index = ["Research", "Name", "Institution", "Method", "Date [d-m-y]"]


    specs = df([specs]).T #, columns=index, index=["General_info"])
    specs.columns = ["General_info"]
    print(specs)


    return(specs)
