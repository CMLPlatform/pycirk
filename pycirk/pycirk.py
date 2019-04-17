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
from pycirk.results import Results
from pycirk.pycirk_settings import Settings
from pycirk.make_scenarios import make_counterfactuals as mcf

class Pycirk:
    """
    directory = directory in which you want to work and save

    method = 0 >> Prod X Prod Ind-Tech Assumption Technical Coeff method
    method = 1 >> Prod X Prod Ind-Tech Assumption Market Share Coeff method

    aggregation = 0 is "bi-regional" (EU- ROW) or 1 is None (multi-regional 49 regions)

    From start you can launch all the analysis specifications listed under
    scenarios.xlsx

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
                 aggregation=0, file=None):

        self.settings = Settings(method, make_secondary, save_directory,
                                 aggregation, file)

        self.scen_file = Settings.scenario_file()

        self.baseline = Settings.transform_to_io()

    def run_one_scenario(self, scen_no, results_only=True):
        """
        Run to check specific scenario

        results_only = False, True
            - True, output results for analysis
            - False, output all tables plus results for analysis
        """
        if scen_no in [0, "baseline", "base", None]:
            scen_no = "baseline"
            IO = self.baseline
        else:
            IO = mcf(self.baseline, scen_no, self.scen_file)

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