# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 16:29:23 2016

Description: Outputting scenarios

Scope: Modelling the Circular Economy in EEIO

@author:Franco Donati
@institution:Leiden University CML
"""
import pandas as pd
from pycirk.save_utils import save_outputs
from pycirk import results
from pycirk.pycirk_settings import Settings
from pycirk.make_scenarios import make_counterfactuals as mcf
import os, glob


class Launch:
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

    Methods
    ----------
    scenario_results : int
        Allows to calculate the results for a given specified scenario

        0 = baseline data

    all_results :
        Retrieves all results for all specified scenarios and baseline

    save_results : int and bool
        save all specified analytical results from all scenario and baseline


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
    def __init__(self, method=0, make_secondary=False, save_directory=None,
                 aggregation=1, file=None, test=False):

        self.settings = Settings(method, make_secondary, save_directory,
                                 aggregation, file, test)

        self.settings.create_scenario_file()

        self.scen_file = self.settings.scenario_file()
        self.analysis_specs = self.settings.load_results_params()

        self.baseline = self.settings.transform_to_io()

        self.labels = self.settings.lb

        self.method = method

        if test is False:
            self.specs = None
        else:
            self.specs = self.settings.project_specs(test=True)

    def scenario_results(self, scen_no, output_dataset=False):
        """
        Run to output results of a specified scenario

        Parameters
        ----------
        scen_no: int
            0 = baseline
            1-n = specified scenarios

        output_datase: bool
            If true it will output a dictionary containing all IOT tables in pd.DataFrames

        Output
        ------
        specified results in DataFrame form or a dictionary containing results
        and a dictionary of dataframes containing IO matrices

        """
        if scen_no in [0, "baseline", "base", None]:
            scen_no = "baseline"
            IO = self.baseline
        else:
            IO = mcf(self.baseline, scen_no, self.scen_file, self.labels)

        output = results.iter_thru_for_results(IO, self.analysis_specs,
                                               scen_no, self.labels)
        if output_dataset is True:
            output = {"res": output, "data": IO}

        return output

    def all_results(self):
        """
        Process all scenarios and collects their results together with
        Baseline analysis results

        Output
        ------
        It outputs a pandas.DataFrame with all results
        """

        output = self.scenario_results(0)

        for l in range(self.settings.number_scenarios()+1):
            if l != 0:
                scen_res = self.scenario_results(l)
                output = pd.concat([output, scen_res], axis=1)
        
        return output


    def save_results(self, scen_no=None, output_dataset=False):
        """
        Saves all results in excel format for info and results or in
        pickle format for the dataset

        Parameters
        ----------
        scen_no: int
            0 = baseline

            1-n = specified scenarios

        output_datase: bool
            If true it will output a dictionary containing all IOT tables in
            pd.DataFrames

        Output
        ------
        Default values will save all results from the all_results method
        and they will output only scenario.xlsx and info_and_results.xlsx

        Output_dataset is only possible when scen_no is specified
        in which case it would save also a data.pkl file
        
        scenarios.xlsx : excel file
            scenario settings excel file used for the analysis in the same
            output directory with the results

        info_and_results.xlsx : excel file
            excel file containing general info about project plus the
            results from the analysis

        data.pkl : pickle file
            new modified IO dataset in pickle format
            This is only possible if outputting single scenario (scen_no != None)

        """
        if self.specs is None:
            self.specs = self.settings.project_specs()
        else:
            pass

        if type(scen_no) is int:
            scenario = self.scenario_results(scen_no, output_dataset)
            data = None
        elif scen_no is None:
            scenario = self.all_results()
            data = None
        if output_dataset is True:
            scenario = self.scenario_results(scen_no, output_dataset)
            data = scenario["data"]
            scenario = scenario["res"]


        save_outputs(scenario, self.settings.save_directory, self.specs,
                     scen_no, data)
        
    def delete_previous_IO_builds(self):
        """
        Call this method if you want to elinate all previous 
        IO databases created by pycirk. SUTs database is not affected.
        """
        for filename in glob.glob("pycirk//data//mrIO*"):
            os.remove(filename) 