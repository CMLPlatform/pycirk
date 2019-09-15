# -*- coding: utf-8 -*-
"""
Created on Wed Feb 20 16:29:23 2019

Description: Setting parameters for pycirk

Scope: Modelling the Circular Economy in EEIO

@author:Franco Donati
@institution:Leiden University CML
"""
import os
import pandas as pd
import numpy as np
import pickle
from sys import platform
from shutil import copyfile
import os.path as ospt
from pycirk.make_secondary_flows import make_secondary as ms
from pycirk.transformation_methods import Transform
from pycirk.make_scenarios import make_counterfactuals
from pycirk.labels import Labels
from pycirk.organize_io import organizer


class Settings:
    """
    This class allows for to specify the settings for pycirk.

    Parameters
    ----------

    method : int
        SUTs to IO transformation methods

        0 = Prod X Prod Ind-Tech Assumption Technical Coeff method

        1 = Prod X Prod Ind-Tech Assumption Market Share Coeff method

    make_secondary : bool
        modifies SUT so that secondary technologies which process scrap
        materials into primary materials are also available in the IO tables

        False = Don't modify

        True = Modify

    save_directory : str
        directory in which you want to work and save your results

    aggregation : int, bool

        0 = None (multi-regional 49 regions)

        1 = bi-regional (EU- ROW)

    file : bool, str
        allows you to specify where the dataset is placed. None will use the
        default location within the installed package

    test : bool
        if set to true it will run the test settings under under pycirk//tests

    """
    def __init__(self, method=0, make_secondary=False, save_directory="",
                 aggregation=1, file=None, test=False):

        self.method = method  # 0 or 1
        self.make_secondary = make_secondary
        self.file = file
        self.save_directory = save_directory
        self.test = test
        self.aggregation = aggregation
        self.lb = Labels()
        self.directory_labels = ospt.abspath(ospt.join(ospt.dirname(__file__), "labels"))

    def check_expand_directory(self, directory):
        """
        Checking that we are using the right directory for the right OS
        """

        if "linux" in platform or platform == "darwin":
            return os.path.expanduser(directory)

        elif "win" in platform:
            if platform != "darwin":
                return os.path.expanduser(directory)

    def project_specs(self, test=False):
        """
        General specifications for the project, they are also used to mark
        the output files
        """
        if int(self.method) == 0:
            method = "(0) IOTpxpSTA_MSCm"

        elif int(self.method) == 1:
            method = "(1) IOTpxpSTA_TCm"

        if test is True:  # test-path with test scenarios
            print("Running in test mode")
            specs = {"Research": "test",
                     "Name": "test",
                     "Organization": "test",
                     "Method": method
                     }

        elif test is False:
            print("Please enter your project information\n")
            name = input("Author's name:\n")  # e.g. "Franco Donati"
            research = input("Project name:\n")  # e.g. "Modelling the CE"
            institution = input("Institution:\n")  # e.g."Leiden Univ. CML"
            specs = {"research": research,
                     "name": name,
                     "institution": institution,
                     "method": method
                     }
            
        return specs

    def set_save_directory(self):
        """
        It specifies where the scenario file for input is located
        """

        if self.test is True:
            self.save_directory = os.path.abspath("tests/")

        elif self.test is False:

            if self.save_directory == "" or self.save_directory is None:
                g = os.path.join("~", "Documents", "pycirk")

                self.save_directory = self.check_expand_directory(g)

                if os.path.isdir(self.save_directory) is False:
                    os.makedirs(self.save_directory)

    def create_scenario_file(self):
        """
        It creates a new scenario file by copying the original from
        pycirk directory to the new working directory specified by the user
        """

        orig = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            "scenarios.xlsx"))

        self.set_save_directory()
        file_dir = os.path.join(self.save_directory, "scenarios.xlsx")

        if not os.path.isfile(file_dir):
            copyfile(orig, file_dir)

        print(f"\nPlease open {file_dir} to set your analysis and scenarios.",
              "\nReturn to this script after you're done.")

    def create_output_folder(self):
        """
        It creates an output folder where to save analytical results
        This is placed in the user's working directory
        """

        output_folder = os.path.join(self.file_directory(), "outputs")

        if os.path.isdir(output_folder) is True:
            pass
        elif os.path.isdir(output_folder) is False:
            os.makedirs(output_folder)

    def scenario_file(self):
        """
        It returns where the working scenarios.xlsx file is located
        """

        return os.path.join(self.save_directory, "scenarios.xlsx")

    def load_dataset(self, data):
        """
        It loads the baseline dataset
        """
        return pd.read_pickle(data)

    def check_dataset_location(self):
        """
        It identifies where the baseline dataset is located and whether it is
        present in the directory. If an IO database was already created in the
        past then it will just return it's location and type instead of
        transforming the SUTs into IOT anew

        Output
        ------
        A dictionary containing location "loc" and type of format (SUT or IO)
        """

        if self.file is not None:
            return {"loc": self.file, "type": np.nan}

        if self.file is None:

            if self.method in [0, 1]:
                io_file_bi = "data//mrIO_EU_ROW_V3.3.pkl"
                io_file_all = "data//mrIO_V3.3.pkl"

            if self.make_secondary is True:
                io_file_bi = "data//mrIO_EU_ROW_V3.3.sm.pkl"
                io_file_all = "data//mrIO_V3.3.sm.pkl"

            if self.aggregation == 1:
                io = io_file_bi
                sut = "data//mrSUT_EU_ROW_V3.3.pkl"

            elif self.aggregation == 0:
                io = io_file_all
                sut = "data//mrSUT_V3.3.pkl"

            io = ospt.abspath(ospt.join(ospt.dirname(__file__), io))
            sut = ospt.abspath(ospt.join(ospt.dirname(__file__), sut))

            if os.path.exists(io) is False and os.path.exists(sut) is False:
                raise FileNotFoundError("Download database from repository " +
                                        "or ask for a copy through " +
                                        "f.donati@cml.leidenuniv.nl " +
                                        "and add it to " +
                                        ospt.join(ospt.dirname(__file__)))

            elif os.path.exists(io) is True:
                data = io
                typ = "io"
            elif os.path.exists(sut) is True:
                data = sut
                typ = "sut"

            return {"loc": data, "type": typ}

    def transform_to_io(self):
        """
        Transforms the SUT dataset into an IO system

        If the user specified to make secondary material processing apparent
        then it will launch the function to modify the database

        If an IO from the same transformation method exists, then it will load
        that one instead

        If a pre-existing IO is not present then it will save the transformed
        dataset in the directory. This is done to spead up processing time.

        Output
        ------
        An object containing all the fundamental IO matrices to begin the
        analysis and scenarios.
        """

        dataset_spec = self.check_dataset_location()

        loc = dataset_spec["loc"]
        typ = dataset_spec["type"]

        try:
            data = self.load_dataset(loc)
        except Exception:
            raise FileNotFoundError("Your database could not be opened" +
                                    " check your file:\n\n" + loc)

        if typ == "sut":
            if self.make_secondary is True:
                data = ms(data)
                extension = ".sm.pkl"
            else:
                extension = ".pkl"

            SUTs = Transform(data)
            self.lb.save_labels(data, self.directory_labels)
            del(data)
            #  Transform SUT to IOT
            if self.method == 0:
                IOT = SUTs.IOTpxpSTA_TCm()
            elif self.method == 1:
                IOT = SUTs.IOTpxpSTA_MSCm()

            del(SUTs)

            if self.aggregation in [0, None]:
                pickle_name = "pycirk//data//mrIO_V3.3" + extension
            elif self.aggregation == 1:
                pickle_name = "pycirk//data//mrIO_EU_ROW_V3.3" + extension
            # saving the IO tables to avoid rebuilding them all the time

            IOT = organizer(IOT)
            IOT = self.lb.relabel_to_save(IOT, self.method,
                                          self.directory_labels)

            with open(pickle_name, "wb") as w:
                pickle.dump(IOT, w, 2)  # pickling

        elif typ == "io":
                self.lb.save_labels(data, self.directory_labels)
                IOT = data
                del(data)

        self.assign_labels_to_class()

        return IOT

    def set_SUTs(self):
        
        if self.aggregation == 1:
            loc = "data//mrSUT_EU_ROW_V3.3.pkl"

        elif self.aggregation == 0:
            loc = "data//mrSUT_V3.3.pkl"

        loc = ospt.abspath(ospt.join(ospt.dirname(__file__), loc))

        try:
            data = self.load_dataset(loc)
        except Exception:
            raise FileNotFoundError("Your database could not be opened" +
                                    " check your file:\n\n" + loc)
        return Transform(data)


    def assign_labels_to_class(self):
        """
        Assigns all labels to their respective attributes in the Labels class
        These are used througout the program to find coordinates and 
        label results
        """

        all_labels = self.lb.organize_unique_labels(self.directory_labels)

        try:
            self.lb.country_labels = all_labels.products.country_code
        except Exception:
            pass

        self.lb.region_labels = all_labels.products.region
        self.lb.product_labels = all_labels.products
        self.lb.industry_labels = all_labels.industries
        self.lb.W_labels = all_labels.primary
        self.lb.E_labels = all_labels.emis
        self.lb.R_labels = all_labels.res
        self.lb.M_labels = all_labels.mat
        self.lb.Y_labels = all_labels.fin_dem
        self.lb.Cr_E_labels = all_labels.car_emis
        self.lb.Cr_R_labels = all_labels.car_res
        self.lb.Cr_M_labels = all_labels.car_mat
        self.lb.Cr_W_labels = all_labels.car_prim

    def set_IO_scenario(self, data, scen_no):
        """
        Class the functions to modify the IO database according to your
        scenario specifications
        """

        if scen_no == 0:
            scenario = self.transform_to_io() # I will likely delete this later
        else:
            scenario = make_counterfactuals(data, scen_no, self.scenario_file(), self.lb)

        return self.lb.relabel_to_save(scenario, self.method, "pycirk//labels/")

#    def set_SUTs_scenario(self, data, scen_no):
#
#        if scen_no == 0:
#            scenario = data # I will likely delete this later
#        else:
#            scenario = make_counterfactuals_SUT(data, scen_no, self.scenario_file(), self.lb)
#
#        return self.lb.relabel_to_save(scenario, self.method, "pycirk//labels/")

    def load_results_params(self):
        return pd.read_excel(self.scenario_file(), sheet_name="analyse", header=3)

    def number_scenarios(self):
        scen_file = pd.ExcelFile(self.scenario_file())
        scenarios = [l for l in scen_file.sheet_names if l.startswith("scenario_")]
        return len(scenarios)
