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
from pycirk.organize_io import Organize_IO
from pycirk.make_secondary_flows import make_secondary as ms
from pycirk.transformation_methods import Transform


class Settings:
    """
    This class allows for to specify the settings for pycirk.
    """
    def __init__(self, method=0, make_secondary=False, save_directory="",
                 aggregation=0, file=None, test=False):

        self.method = int(method)  # 0 or 1
        self.make_secondary = make_secondary
        self.file = file
        self.save_directory = save_directory
        self.test = test
        self.aggregation = aggregation

    def check_expand_directory(self, directory):
        """
        Checking that we are using the right directory for the right OS
        """

        if "linux" in platform or platform == "darwin":
            directory = os.path.expanduser(directory)

        elif "win" in platform:
            if platform != "darwin":
                directory = os.path.expanduser(directory)

        return(directory)

    def project_specs(self, test=False):
        """
        General labelling of the project
        """

        if test is True:  # test-path with test scenarios
            print("Running in test mode")
            specs = {"research": "test",
                     "name": "test",
                     "institution": "test",
                     }

        if test is False:
            name = input("Author's name:\n")  # e.g. "Franco Donati"
            research = input("Project name:\n")  # e.g. "Modelling the CE"
            institution = input("Institution:\n")  # e.g."Leiden Univ. CML"
            specs = {"research": research,
                     "name": name,
                     "institution": institution,
                     }

        return(specs)

    def file_directory(self):
        """
        It specifies where the scenario file for input is
        """

        if self.test is True:
            directory = os.path.abspath("tests/")

        elif self.test is False:

            if self.save_directory == "":
                directory = self.check_expand_directory("~/Documents/pycirk/")

            elif self.save_directory != "":
                if os.path.isdir(self.save_directory) is True:
                    pass
                elif os.path.isdir(self.save_directory) is False:
                    os.makedirs(self.save_directory)

                directory = self.save_directory

        return(directory)

    def create_scenario_file(self):

        orig = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            "scenarios.xls"))

        directory = self.file_directory()
        file = directory + "scenarios.xls"

        if not os.path.isfile(file):
            copyfile(orig, file)

        print("\nPlease open ", file, " to set your analysis and scenarios.",
              "\n\nReturn to this script after you're done.")

    def create_output_folder(self):

        output_folder = self.file_directory() + "/outputs/"

        if os.path.isdir(output_folder) is True:
            pass
        elif os.path.isdir(output_folder) is False:
            os.makedirs(output_folder)

    def scenario_file(self):

        scen_file = self.file_directory() + "scenarios.xls"

        return(scen_file)

    def load_dataset(self, data):

        data = pd.read_pickle(data)

        return(data)

    def check_dataset_location(self):

        if self.file is not None:
            data_loc = {"loc": self.file, "type": np.nan}

        if self.file is None:

            if self.method in [0, 1]:
                io_file_bi = "data//mrIO_EU_ROW_V3.3.pkl"
                io_file_all = "data//mrIO_V3.3.pkl"

            if self.make_secondary is True:
                io_file_bi = "data//mrIO_EU_ROW_V3.3.x.pkl"
                io_file_all = "data//mrIO_V3.3.x.pkl"

            if self.aggregation == 0:
                io = io_file_bi
                sut = "data//mrSUT_EU_ROW_V3.3.pkl"

            elif self.aggregation == 1:
                io = io_file_all
                sut = "data//mrSUT_V3.3.pkl"

            io = ospt.abspath(ospt.join(ospt.dirname(__file__), io))
            sut = ospt.abspath(ospt.join(ospt.dirname(__file__), sut))

            if os.path.exists(io) is False and os.path.exists(sut) is False:
                raise FileNotFoundError("Download database from exiobase.eu " +
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

            data_loc = {"loc": data, "type": typ}

        return(data_loc)

    def transform_to_io(self):

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
                extension = ".x.pkl"
            else:
                extension = ".pkl"

            SUTs = Transform(data)

        #  Transform SUT to IOT
            if self.method == 0:
                IOT = SUTs.IOTpxpSTA_TCm()
            elif self.method == 1:
                IOT = SUTs.IOTpxpSTA_MSCm()

            IOT = Organize_IO(IOT)

            if self.aggregation == 0:
                pickle_name = "pycirk//data//mrIO_EU_ROW_V3.3" + extension
            elif self.aggregation == 1:
                pickle_name = "pycirk//data//mrIO_V3.3" + extension
            # saving the IO tables to avoid rebuilding them all the time

            datatopkl = IOT.__dict__
            with open(pickle_name, "wb") as w:
                pickle.dump(datatopkl, w, 2)  # pickling
            
            #os.remove(pickle_name)
        elif typ == "io":
                IOT = Organize_IO(data)
        
        

        return(IOT)
