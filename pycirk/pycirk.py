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
import pickle
from sys import platform
from shutil import copyfile
import os.path as ospt
from pycirk.save_ import Save
from pycirk.results import Results
from pycirk.base_n_scen import Base_n_scen
from pycirk.make_secondary_flows import make_secondary as ms
from pycirk.SUTtoIOT import Transform
import matplotlib.pyplot as plt


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
    def __init__(self, method=0, make_secondary=False, save_directory="",
                 aggregation="bi-regional", file=None):

        self.method = int(method)  # 0 or 1

        orig = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            "scenarios.xls"))

        self.aggregation = aggregation  # biregional or None=multiregional

        if save_directory == "":
            # here we try to indentify on which platform we are working
            # and specifying default folders
            if "linux" in platform or platform == "darwin":
                save_directory = os.path.expanduser("~/Documents/pycirk/")

            elif "win" in platform:
                if platform != "darwin":
                    save_directory = os.path.expanduser("~/Documents/pycirk/")
                else:
                    save_directory = input("Please specify the directory: ")
            else:
                save_directory = input("Please specify the directory: ")
                # checking if the file already exists else copying settings to
                # the output folder
            if not os.path.isfile(save_directory + "scenarios.xls"):
                os.makedirs(save_directory)
                copyfile(orig, save_directory + "scenarios.xls")

        elif save_directory != "test" and "":
            # origin of scenarios.xls file
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)
                copyfile(orig, save_directory + "scenarios.xls")
            else:
                pass

        elif save_directory == "test":  # test path contains test scenarios
            save_directory = os.path.abspath("tests/")
            print("test")
            self.specs = {"research": "test",
                          "name": "test",
                          "institution": "test",
                          }

        if save_directory != "test":
            name = input("Author's name:\n")  # e.g. "Franco Donati"
            research = input("Project name:\n")  # e.g. "Modelling the CE"
            institution = input("Institution:\n")  # e.g."Leiden Univ. CML"
            self.specs = {"research": research,
                          "name": name,
                          "institution": institution,
                          }

        print("\nPlease open scenarios.xls under ", save_directory,
              " to set your work.\n\nReturn to this script after you are",
              "done setting up your scenarios.")

        # defines a directory for outputs when saving
        self.save_directory = save_directory + "/outputs/"
        self.scen_file = pd.ExcelFile(save_directory + "scenarios.xls")

        if file is None:
            if method in [0, 1]:
                io_file_bi = "data//mrIO_EU_ROW_V3.3.pkl"
                io_file_all = "data//mrIO_V3.3.pkl"
            if make_secondary is True:
                io_file_bi = "data//mrIO_EU_ROW_V3.3.x.pkl"
                io_file_all = "data//mrIO_V3.3.x.pkl"

            if aggregation == "data//bi-regional":
                file = io_file_bi
                sut = "data//mrSUT_EU_ROW_V3.3.pkl"
            elif aggregation is None:
                file = io_file_all
                sut = "data//mrSUT_V3.3.pkl"

            file = ospt.abspath(ospt.join(ospt.dirname(__file__), file))
            sut = ospt.abspath(ospt.join(ospt.dirname(__file__), sut))

            if os.path.exists(file):
                print(file)
                data = file
                exists = True
            else:
                print(sut)
                data = sut
                exists = False

        try:
            self.data = pd.read_pickle(data)
        except Exception:
            raise FileNotFoundError("Download database from exiobase.eu " +
                                    "or ask for a copy through " +
                                    "f.donati@cml.leidenuniv.nl " +
                                    "and add it to " +
                                    ospt.join(ospt.dirname(__file__)))

        if exists is False:
            self.exists = False
            self.SUTs = Transform(data)

            #  Transform SUT to IOT
            if int(method) == 0:
                self.IOT = self.SUTs.IOTpxpSTA_TCm()
            elif int(method) == 1:
                self.IOT = self.SUTs.IOTpxpSTA_MSCm()

        elif exists is True:
            self.IOT = data
            self.exists = True

        if exists is False:
            # making secondary flows apparent
            if make_secondary is True:
                self.data = ms(data)
                self.bns = Base_n_scen(self.data)
                self.IO = self.bns.IOT
                pickle_name = "pycirk//data//mrIO_V3.3.x.pkl"
            else:
                self.bns = Base_n_scen(self.data)
                self.IO = self.bns.baseIOT()
                pickle_name = "pycirk//data//mrIO_V3.3.pkl"

            # saving the IO tables to avoid rebuilding them all the time
            w = open(pickle_name, "wb")
            pickle.dump(self.IO, w, 2)  # pickling
            w.close()

        elif exists is True:
            self.bns = Base_n_scen(self.data)
            self.IO = self.bns.IOT

    def run_one_scenario(self, scen_no, results_only=True):
        """
        Run to check specific scenario

        results_only = False, True
            - True, output results for analysis
            - False, output all tables plus results for analysis
        """
        if scen_no in [0, "baseline", "base", None]:
            scen_no = "baseline"
            IO = self.IO
        else:
            IO = self.bns.sceneIOT(self.IO, scen_no, self.scen_file)

        output = Results.one_scen(IO, scen_no, results_only)

        return(output)

    def all_results(self, results_only=True):
        """
        Output all results in a table
        Take a dictionary of all scenarios' results
        and organise them in table
        """

        if results_only is False:
            output = {}

        n = 1
        while n <= len(self.sheets):
            if n == 1:
                IOT = self.run_one_scenario(n, results_only)
                t = Results.one_scen(IOT, n, results_only)
                if results_only is False:
                    name = "sc_" + str(n)
                    output[name] = t

            elif n > 1:
                t2 = self.one_scen(n, results_only)

                if results_only is True:
                    t = pd.concat([t, t2], axis=1)

                elif results_only is False:
                    name = "sc_" + str(n)
                    output[name] = t2
            n += 1

        baseline = Results.one_scen("baseline", results_only)

        if results_only is False:
            output["baseline"] = baseline
        else:
            output = pd.concat([baseline, t], axis=1).fillna("")

        return(output)

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
