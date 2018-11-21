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
import pickle as pk
from shutil import copyfile
from pandas import DataFrame as df
now = datetime.datetime.now()


class Save:
    """
    Contains various methods to output results from analysis and modelling
    """

    def __init__(self, specs, directory, method):

        s = "_"
        self.time = s.join([str(now.year), str(now.month), str(now.day),
                            str(now.hour), str(now.minute)])

        self.directory_or = directory
        self.directory_out = directory + self.time + "/"

        if int(method) == 0:
            self.method = "(0) IOTpxpSTA_MSCm"
        elif int(method) == 1:
            self.method = "(1) IOTpxpSTA_TCm"
        self.year, self.month, self.day = str(now.date()).split("-")

        self.specs = specs

    def gen_specs(self, scen_no):
        """
        Assembles general specifications e.g. authors, institution etc
        """

        research = self.specs["research"]
        name = self.specs["name"]
        institution = self.specs["institution"]

        index = ["Research", "Name", "Institution", "Date [d-m-y]",
                 "Scenario no", "Method"]
        timemark = "/".join([self.day, self.month, self.year])
        general = df([research, name, institution, timemark, scen_no,
                     self.method], index=index, columns=["General_info"])

        return(general)

    def save_(self, data, scen_no):
        """
        It saves results into a previously specified directory
        """

        if scen_no in ["baseline", 0, "base"]:
            scen_no = "baseline"
            path = self.directory_out + "baseline" + "/"
        elif scen_no.startswith("sc"):
            scen_no = str(scen_no)
            path = self.directory_out + "scenario_" + scen_no[3:] + "/"
        else:
            path = self.directory_out

        if not os.path.exists(path):
            os.makedirs(path)

        data["specs"] = self.gen_specs(scen_no)

        for l, value in data.items():
            if scen_no == "baseline" or scen_no.startswith("sc"):
                    value.to_csv(path_or_buf=path +
                                 "_".join([scen_no, l, self.time]) + ".txt")
            else:
                value.to_csv(path_or_buf=self.directory_out +
                             "_".join([self.time, l]) + ".txt")

        copyfile(self.directory_or + "../scenarios.xls", self.directory_out +
                 "_".join([self.time, "scenario_settings"]) + ".xls")

        w = open(self.directory_out + self.time + "_data.pkl", "wb")
        pk.dump(data, w, 2)

        w.close()

    def save_everything(self, data):
        """
        saves all scenarios + baseline + comparable file
        """
        for l, v in data.items():
            out = self.save_(v, l)

        return(out)

    def save_results(self, data):
        """
        Save one excel with all results
        """
        data = {"results": data}

        out = self.save_(data, "summary_results")

        return(out)
