# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 16:29:23 2016

Description: Outputting scenarios

Scope: Modelling the Circular Economy in EEIO

@author:Franco Donati
@institution:Leiden University CML
"""
import os
import numpy
import pandas as pd
from sys import platform
from shutil import copyfile
import os.path as ospt
from pycirk.save_ import Save
from pycirk.results import Results
import matplotlib.pyplot as plt
from pycirk.make_secondary_flows import make_secondary as ms


class Start:
    """
    directory = directory in which you want to work and save

    method = 0 >> Prod X Prod Ind-Tech Assumption Technical Coeff method
    method = 1 >> Prod X Prod Ind-Tech Assumption Market Share Coeff method

    aggregation = "bi-regional" (EU- ROW) or None (multi-regional 49 regions)

    From start you can launch all the analysis specifications listed under
    scenarios.xls

    All directories and base data are specified in dirs.py

    Results will be saved in the output folder

    The programme only considers two regions EU and Rest-Of-World (ROW)

    Permitted SUT transformation Methods are

    method = 0 >> Prod X Prod Ind-Tech Assumption Technical Coeff method
    method = 1 >> Prod X Prod Ind-Tech Assumption Market Share Coeff method

    results_only = True >> output only results (spec'd in scenarios.xls)
    results_only = False >> output all IOTs and results

    scen_no = 0 - n (0 = baseline)
        n = is number of scenarios specified by sheet in scenarios.xls
        "scenario_1" is also allowed for scenarios
        None, 0, base and baseline are also accepted for baseline
    """
    def __init__(self, method=0, directory="", aggregation="bi-regional",
                 file=None, make_secondary=False):

        self.method = int(method)  # 0 or 1

        self.directory = directory

        orig = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            "scenarios.xls"))
        print(orig)
        if self.directory == "":
            # here we try to indentify on which platform we are working
            # and specifying default folders
            if "linux" in platform or platform == "darwin":
                self.directory = os.path.expanduser("~/Documents/pycirk/")

            elif "win" in platform:
                if platform != "darwin":
                    self.directory = os.path.expanduser("~/Documents/pycirk/")
                else:
                    self.directory = input("Please specify the directory: ")
            else:
                self.directory = input("Please specify the directory: ")
                # checking if the file already exists else copying settings to
                # the output folder
            if not os.path.isfile(self.directory + "scenarios.xls"):
                os.makedirs(self.directory)
                copyfile(orig, self.directory + "scenarios.xls")

        elif directory != "test" and "":
            # origin of scenarios.xls file
            if not os.path.exists(self.directory):
                os.makedirs(self.directory)
                copyfile(orig, self.directory + "scenarios.xls")
            else:
                pass

        elif directory == "test":  # test path contains preset test scenario
            self.directory = os.path.abspath("tests/")
            print("test")
            self.specs = {"research": "test",
                          "name": "test",
                          "institution": "test",
                          }

        if directory != "test":
            name = input("Author's name:\n")  # e.g. "Franco Donati"
            research = input("Project name:\n")  # e.g. "Modelling the CE"
            institution = input("Institution:\n")  # e.g."Leiden Univ. CML"
            self.specs = {"research": research,
                          "name": name,
                          "institution": institution,
                          }

        print("\nPlease open scenarios.xls under ", self.directory,
              " to set your work.\n\nReturn to this script after you are",
              "done setting up your scenarios.")

        # defines a directory for outputs when saving
        self.save_directory = self.directory + "/outputs/"
        self.scen_file = self.directory + "scenarios.xls"
        print(self.scen_file)

        self.aggregation = aggregation  # biregional or None=multiregional

        # uploading data
        if file is not None:
            self.data = pd.read_pickle(file)

        else:
            # choosing aggregation type (bi-regional or full 49 regions)
            if aggregation == "bi-regional":
                #  SUT biregional EU-ROW
                file = ospt.abspath(ospt.join(ospt.dirname(__file__),
                                              "mrSUT_EU_ROW_V3.3.pkl"))
            elif aggregation is None:
                # SUT full 2011 data
                file = ospt.abspath(ospt.join(ospt.dirname(__file__),
                                              "mrSUT_V3.3.pkl"))
            try:
                self.data = pd.read_pickle(file)
            except Exception:
                raise FileNotFoundError("Download database from exiobase.eu " +
                                        "or ask for a copy through " +
                                        "f.donati@cml.leidenuniv.nl " +
                                        "and add it to " +
                                        ospt.join(ospt.dirname(__file__)))

        # making secondary flows apparent
        if make_secondary is True:
            self.data = ms(self.data)

        self.init_res = Results(self.data, self.method, self.scen_file)

    def run_one_scenario(self, scen_no, results_only=True):
        """
        Run to check specific scenario

        results_only = False, True
            - True, output results for analysis
            - False, output all tables plus results for analysis
        """
        scenario = self.init_res.one_scen(scen_no, results_only)

        return(scenario)

    def all_results(self):
        """
        Output all results in a table
        """
        results_table = self.init_res.table_res()

        return(results_table)

    def save_one_scenario(self, scen_no, results_only=False):
        """
        Output all results in a table
        """
        init_save = Save(self.specs, self.save_directory, self.method)
        scenario = self.run_one_scenario(scen_no, results_only)
        init_save.save_(scenario, scen_no)

    def save_all_scenarios(self):
        """
        Save all results in separate files and sheets
        data e.g. all_results.all_tables
        """
        init_save = Save(self.specs, self.save_directory, self.method)
        data = self.init_res.table_res(False)
        init_save.save_everything(data)

    def save_results(self):
        """
        Save results
        """
        init_save = Save(self.specs, self.save_directory, self.method)
        data = self.all_results()
        init_save.save_results(data)

    def save_everything(self):
        """
        Save all scenarios and results
        """
        self.save_results()
        self.save_all_scenarios()

    def plot_results(self, results):
        """
        Plots bar graph of the summary results
        """

        labels = list(results.index[1:].values)
        base = results[0]
        y_pos = numpy.arange(len(results[1:]))
        difference = -(1-results.iloc[1:] / base)*100

        title = "Difference from baseline"
        sub_title = results.name

        plt.bar(y_pos, difference, width=0.35, align='center', alpha=0.75)
        plt.xticks(y_pos, labels)
        plt.xlabel("Scenarios")
        plt.ylabel("%")  # sub_title[-1])
        plt.title(str(title) + "\n" + str(sub_title))
        plt.show()


if __name__ == "__main__":
    Start
