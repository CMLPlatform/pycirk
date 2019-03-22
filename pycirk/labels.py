# -*- coding: utf-8 -*-
"""
Created on sat Jan 28 2017

Description: Labelling elements for SUTs and IOTs

Scope: Modelling the Circular Economy in EEIO

@author:Franco Donati
@institution:Leiden University CML
"""

from pandas import DataFrame as df
from pandas import MultiIndex as mi
from pandas import read_csv
from munch import Munch
import warnings


class Labels:
    def __init__(self):
        self.no_countries = None
        self.no_cat = None
        self.no_E_cat = None

    def calc_no_countries(self, labels):

    def list_of_countries(self, labels):

    def list_of_cat(self, labels):



    def calc_no_categories(self, labels):
        no_cat = labels[]

    def load_labels(self, directory):

        try:
            ind = read_csv(directory + "/industry.csv")  # with unit column
        except Exception:
            ind = None

        try:
            prod = read_csv(directory + "/products.csv")  # with unit column
        except Exception:
            prod = None

        primary = read_csv(directory + "/factor_inputs.csv")
        fin_dem = read_csv(directory + "/final_demand.csv")
        emis = read_csv(directory + "/emissions.csv")
        res = read_csv(directory + "/resources.csv")
        mat = read_csv(directory + "/materials.csv")

        car_emis = read_csv(directory + "/charact_emissions.csv")
        car_res = read_csv(directory + "/charact_resources.csv")
        car_mat = read_csv(directory + "/charact_materials.csv")
        car_prim = read_csv(directory + "/charact_factor_inputs.csv")

        labels = {"ind": ind,
                  "prod": prod,
                  "primary": primary,
                  "fin_dem": fin_dem,
                  "emis": emis,
                  "res": res,
                  "mat": mat,
                  "car_emis": car_emis,
                  "car_res": car_res,
                  "car_mat": car_mat,
                  "car_prim": car_prim}
        return(labels)

    def get_labels(matrix):
        """
        Collects labels from a dataframe
        """
        try:
            output = matrix.index.to_frame(index=False)

            # print("ind",matrix.index[0])
        except Exception:
            # this exception is here only in the case the multi-index is
            # as a list or flat strings instead of an actual multi-index
            output = df(list(matrix.index)).copy()

        return(output)

    def save_labels(self,data, directory):

        try:
            get_labels(data["V"].T).to_csv(directory + "industry.csv", index=False)  # with unit column
        except Exception:
            pass

        get_labels(data["Cr_E_k"], 0).to_csv(directory + "/charact_emissions.csv", index=False)
        get_labels(data["Cr_R_k"], 0).to_csv(directory + "/charact_resources.csv", index=False)
        get_labels(data["Cr_M_k"], 0).to_csv(directory + "/charact_materials.csv", index=False)
        get_labels(data["Cr_W_k"], 0).to_csv(directory + "/charact_factor_inputs.csv", index=False)
        get_labels(data["Y"], 0).to_csv(directory + "/products.csv", index=False)  # with unit column
        get_labels(data["W"], 0).to_csv(directory + "/factor_inputs.csv", index=False)
        get_labels(data["Y"], 1).to_csv(directory + "/final_demand.csv", index=False)
        get_labels(data["E"], 0).to_csv(directory + "/emissions.csv", index=False)
        get_labels(data["R"], 0).to_csv(directory + "/resources.csv", index=False)
        get_labels(data["M"], 0).to_csv(directory + "/materials.csv", index=False)

    def relabel_to_save(data, trans_method):
        """
        This function makes sure that everything is labeled in IOT tables

        trans_method = 0 is prod x prod , 1 is ind x ind
        """
        lb = Munch(load_labels())

        if trans_method in [0, 1]:
            cat = lb.prod
        elif trans_method not in [0, 1]:
            cat = lb.ind

        # Relabel Main IOT elements
        data.S = relabel(data.S, cat.iloc[:, :4], cat)
        #data.L = relabel(data.L, cat.iloc[:, :4], cat.iloc[:, :4])
        #data.A = relabel(data.A, cat, cat)
        data.Y = relabel(data.Y, lb.fin_dem, cat)
        #data.W = relabel(data.W, cat.iloc[:, :4], lb.primary)
        data.w = relabel(data.w, cat, lb.primary)

        # Labeling final demand extensions' intensities
        data.Ye = relabel(data.Ye, lb.fin_dem, lb.emis)
        data.Yr = relabel(data.Yr, lb.fin_dem, lb.res)
        data.Ym = relabel(data.Ym, lb.fin_dem, lb.mat)

        # Inter-trans extensions' intensities
        data.e = relabel(data.e, cat, lb.emis)
        data.r = relabel(data.r, cat, lb.res)
        data.m = relabel(data.m, cat, lb.mat)

        # label q
        data.x = relabel(data.x, "x", cat)
        # label balance verification
        ver_label = "balance (x_out/x_in) - % - 100=balanced - 0=NaN no values"
        data.ver_base = relabel(data.ver_base, ver_label, cat.iloc[:, :4])

        # Relabel Inter-trans extensions
        data.E = relabel(data.Be, cat.iloc[:, :4], lb.emis)
        data.R = relabel(data.Br, cat.iloc[:, :4], lb.res)
        data.M = relabel(data.Bm, cat.iloc[:, :4], lb.mat)

        # Relabel characterized extensions
        data.Cr_E = relabel(data.Cr_E, cat.iloc[:, :4], lb.car_emis)
        data.Cr_R = relabel(data.Cr_R, cat.iloc[:, :4], lb.car_res)
        data.Cr_M = relabel(data.Cr_M, cat.iloc[:, :4], lb.car_mat)
        data.Cr_W = relabel(data.Cr_W, cat.iloc[:, :4], lb.car_prim)

        # Labeling final demand extensions
        data.YE = relabel(data.YE, lb.fin_dem.iloc[:, :4], lb.emis)
        data.YR = relabel(data.YR, lb.fin_dem.iloc[:, :4], lb.res)
        data.YM = relabel(data.YM, lb.fin_dem.iloc[:, :4], lb.mat)

        # Relabel characterized final demand extensions
        data.Cr_YE = relabel(data.Cr_YE, lb.fin_dem, lb.car_emis)
        data.Cr_YE = relabel(data.Cr_YR, lb.fin_dem, lb.car_res)
        data.Cr_YE = relabel(data.Cr_YM, lb.fin_dem, lb.car_mat)

        return(data)

    def apply_labels(matrix, labels, axis=0):
        """
        Applies labels to a dataframe
        axis = 0 => Index
        axis = 1 => columns
        """
        if axis == 0:  # apply index
            matrix.index = mi.from_arrays(labels.values.T)
            matrix.index.names = labels.columns
        elif axis == 1:  # collects columns
            matrix.columns = mi.from_arrays(labels.values.T)
            matrix.columns.names = labels.columns

        return(matrix)


    def relabel(M, column_labels, index_labels):
        """
        Processes apply_labels and apply _names together
        """
        M = df(M)

        try:
            M = apply_labels(M, column_labels, axis=1)  # columns
        except Exception:
            # in case a string is passed for column label for a vector
            M.columns = [column_labels]
        M = apply_labels(M, index_labels, axis=0)  # index

        return(M)
