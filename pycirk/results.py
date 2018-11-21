# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 09:26:43 2017

Description: module to perform results analysis

Scope: Modelling the Circular Economy in EEIO

@author:Franco Donati
@institution:Leiden University CML, TU Delft TPM
"""
import pandas as pd
from pandas import DataFrame as df
from pandas import MultiIndex as mi
import warnings
from pycirk.base_n_scen import Base_n_scen
from pycirk.labels import positions
warnings.simplefilter(action='ignore', category=FutureWarning)


class GatherResults:
    """
    Group results for a specific scenario or all scenarios + baseline
    """
    def __init__(self, data, method, scen_file):

        scenarios = pd.ExcelFile(scen_file)
        self.method = method
        sheet_names = scenarios.sheet_names
        self.sheets = [f for f in sheet_names if f.startswith("scenario_")]
        self.bns = Base_n_scen(data, method)
        self.base = self.bns.baseIOT()
        self.analyse = pd.read_excel(scen_file, "analyse", header=3)
        self.scen_file = scen_file

    def retrieve_specified_data(self, data, spec_row, scen_no):
        """
        Separate, collect and rename results for base and scenarios according
        to specifications under th sheet "analysis" in scenarios.xls

        data = any IOT table
        spec_row = row in the scenarios sheet specifying settings
        scen_no = name of the scenario
        """

        pd.options.display.float_format = '{:,.4f}'.format

        D = df()

        M_name = spec_row["matrix"]  # matrix of reference
        o_p = spec_row["o_p"]  # category of exiobase to analyse (rows)
        o_r = spec_row["o_r"]  # region of exiobase to analyse (rows)

        d_p = spec_row["d_p"]  # baseline cat. for comparison (columns)
        d_r = spec_row["d_r"]  # baseline reg. for comparison (columns)

        if pd.isna(o_p) is True:
            o_p = "All"

        if pd.isna(o_r) is True:
            o_r = "All"

        if pd.isna(d_p) is True:
            d_p = "All"

        if pd.isna(d_r) is True:
            d_r = "All"

        # doing some general checking of the inputs
        if "Y" in M_name:
            if any(item in d_p for item in ["I_", "F_"]) is False:
                if pd.isna(d_p) is True:
                    raise ValueError("If the matrix concerns final demand" +
                                     "d_p can only be on of Final Dem. cat." +
                                     "(e.g. F_HOUS or I_EXP). You selected "
                                     + d_p)
                else:
                    d_p = "All"
        M = data[M_name]  # Call specific matrix from which to select

# =============================================================================
#          getting the labels so I can look through them later
#          Note to self, this is the second or third time I repeat these
#          lines "ind" and "col" maybe I should just write a function for it
# =============================================================================
        ind = M.index.to_frame(False)
        col = M.columns.to_frame(False)

#        if scen_no == "baseline":
        o = positions(ind, o_r, o_p)  # finding the positions
        d = positions(col, d_r, d_p)
        key = [M_name, o_p, o_r, d_p, d_r]  # make labels for results
#
#        else:
#            o = positions(ind, o_r, o_p)
#            d = positions(col, d_r1, d_p1)
#            key = [M_name, o_p, o_r, d_p1, d_r1]  # making labels for results

        if o.size == 0:
            select = M.iloc[:, d]
        elif d.size == 0:
            select = M.iloc[o, :]
        else:
            select = M.iloc[o, d]

# =============================================================================
#         This part sums the results. If I didn't sum them, I couldn't
#         provide I nice summary at the end. If the user wants to look at
#         disaggregated data, they can just output the full tables and
#         look through them themselves
# =============================================================================

        select = df([select.values.sum()])

        #  relabelling
        try:
            # this is added to make sure that results concerning coefficients
            # show the correct unit
            # if the unit is not specified then it will place an empty str
            units = ind["unit"].iloc[o].drop_duplicates().values.item(0)
            if M_name.startswith(("R", "A")):
                if units != "":
                    units = units + "/M.EUR"
                else:
                    pass
            else:
                pass

            key.append(units)

        except Exception:
            key.append("")

        key_names = ["matrix", "o_category", "o_region", "d_category",
                     "d_region", "unit"]

        key = df(str(l) for l in key)  # just labelling

        select = select.reset_index(drop=True)
        select.columns = mi.from_arrays(key.values, names=key_names)

        if D.size == 0:
            D = select
        else:
            D = pd.concat([D, select], axis=1)

        return(D)

    def iter_thru_for_results(self, data, scen_no):
        """
        filter policy interventions from scenario file according to specified
        matrix and return the respective matrix with it
        Output only specified (see scenario.xls) results to be analysed
        """
        results = df()

        for l, v in self.analyse.iterrows():
            res = self.retrieve_specified_data(data, v, scen_no)
            if results.size == 0:
                results = res
            else:
                results = pd.concat([results, res], axis=1)

        return(results)


class Results:
    """
    Launches analysis, collects and assembles all results
    """
    def __init__(self, data, method, scen_file):
        self.gr = GatherResults(data, method, scen_file)
        self.scen_file = scen_file

    def one_scen(self, scen_no=None, results_only=True):
        """
        Display results for baseline or specific scenario
        """
        if scen_no in [0, "baseline", "base", None]:
            scen_no = "baseline"
            sc = self.gr.base
        else:
            sc = self.gr.bns.sceneIOT(scen_no, self.scen_file)

        results = self.gr.iter_thru_for_results(sc, scen_no).T

        if results_only is True:
            sc = results
            # return(sc)
            if scen_no not in [0, "baseline", "base", None]:
                sc.columns = ["sc_" + str(scen_no)]
            else:
                sc.columns = ["baseline"]

        elif results_only is False:
            if scen_no not in [0, "baseline", "base", None]:
                results.columns = ["sc_" + str(scen_no)]
                s_nam = "scenario_" + str(scen_no)
                sc["settings"] = pd.read_excel(self.scen_file, s_nam, header=1)
            else:
                results.columns = ["baseline"]
            sc["results"] = results

        return(sc)

    def table_res(self, results_only=True):
        """
        Take a dictionary of all scenarios' results
        and organise them in table
        """
        if results_only is False:
            C = {}

        n = 1
        while n <= len(self.gr.sheets):
            if n == 1:
                t = self.one_scen(n, results_only)
                if results_only is False:
                    name = "sc_" + str(n)
                    C[name] = t

            elif n > 1:
                t2 = self.one_scen(n, results_only)

                if results_only is True:
                    t = pd.concat([t, t2], axis=1)

                elif results_only is False:
                    name = "sc_" + str(n)
                    C[name] = t2
            n += 1

        baseline = self.one_scen("baseline", results_only)

        if results_only is False:
            C["baseline"] = baseline
        else:
            C = pd.concat([baseline, t], axis=1).fillna("")

        return(C)
