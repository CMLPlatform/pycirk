# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 16:29:23 2016

Description: Outputting scenarios

Scope: Modelling the Circular Economy in EEIO

@author:Franco Donati
@institution:Leiden University CML
"""
import pandas as pd
from pycirk.save_utils import Save
from pycirk import results
from pycirk.pycirk_settings import Settings
from pycirk.make_scenarios import make_counterfactuals as mcf

class Main:
    """
    Pycirk's main class and methods

    Initialize the pycirk programme to make EEIO scenarios and analysis.
    From here, you can launch all the analysis specifications listed under
    scenarios.xlsx

    Parameters
    ----------
    method : int
        SUTs to IO transformation methods
        0 = Prod X Prod Ind-Tech Assumption Technical Coeff method
        1 = Prod X Prod Ind-Tech Assumption Market Share Coeff method

    make_secondary : bool
        modifies SUT so that secondary technologies which process scrap materials
        into primary materials are also available in the IO tables
        False = Don't modify
        True = Modify

    save_directory : str
        directory in which you want to work and save your results

    aggregation : int, bool
        0 = None (multi-regional 49 regions)
        1 = bi-regional (EU- ROW)

    file : bool, str
        allows you to specify where the dataset is placed. None will use the default
        location within the installed package


    Methods
    ----------
    scenario_results : int
        Allows to calculate the results for a given specified scenario
        0 = baseline data

    all_results :
        Retrieves all results for all specified scenarios and baseline

    save_scenario : int
        save a scenario and specific results

    save_results :
        save all specified analytical results from all scenario and baseline

    save_all:
        Runs save_results + save_scenario for all specified scenarios


    Outputs
    -------
    analysis.xlsx : excel file
        to be found under the default folder on the specified directory
        it allows to specify the parameters for your scenario and analysis

    IO tables : pkl
        IO tables of the specified scenarios, these are located in the output
        folder in the save directory

    results : DataFrame
        results gathered from the processed scenarios and baseline

    """
    def __init__(self, method=0, make_secondary=False, save_directory="",
                 aggregation=1, file=None):

        self.settings = Settings(method, make_secondary, save_directory,
                                 aggregation, file)

        self.settings.create_scenario_file()

        self.scen_file = self.settings.scenario_file()
        self.analysis_specs = self.settings.load_results_params()

        self.baseline = self.settings.transform_to_io()

        self.labels = self.settings.lb

        self.method = method

        self.specs = None

    def scenario_results(self, scen_no):
        """
        Run to output results of a specified scenario

        Parameters
        ----------
        scen_no: int
            0 = baseline
            1-n = specified scenarios

        Output
        ------
        specified results in DataFrame form

        """
        if scen_no in [0, "baseline", "base", None]:
            scen_no = "baseline"
            IO = self.baseline
        else:
            IO = mcf(self.baseline, scen_no, self.scen_file, self.labels)

        output = results.iter_thru_for_results(IO, self.analysis_specs,
                                               scen_no, self.labels)
        return(output)

    def all_results(self):

        output = self.scenario_results(0)

        for l in range(self.settings.number_scenarios()+1):
            if l != 0:
                scen_res = self.scenario_results(l)
                output = pd.concat([output, scen_res], axis=1)
        return(output)


    def save_scenario(self, scen_no, specs=None):
        """
        Output all results in a table
        """
        if self.specs is None:
            self.specs = self.settings.project_specs()
        else:
            pass

        init_save = Save(self.specs, self.settings.file_directory(), self.method)
        scenario = self.scenario_results(scen_no)
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