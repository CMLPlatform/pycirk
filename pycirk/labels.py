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


class Labels:
    def __init__(self):
        self.country_labels = None
        self.region_labels = None
        self.cat_labels = None  # products or industries
        self.W_labels = None
        self.E_labels = None
        self.R_labels = None
        self.M_labels = None
        self.Y_labels = None
        self.Cr_E_labels = None
        self.Cr_M_labels = None
        self.Cr_R_labels = None
        self.Cr_W_labels = None

    def calc_no_of_something(self, labels):
        no_of_something = len(labels.unique())
        return(no_of_something)

    def list_of_something(self, labels):
        list_of_some = labels.unique()
        return(list_of_some)

    def get_unique_labels(self, list_of_labels):

        organize = dict()
        for keys, labels in list_of_labels.items():
            organize[keys] = self.list_of_something(labels)

        count = max(len(labels) for keys, labels in organize.items())
        organize["count"] = count
        
        return(Munch(organize))

    def organize_unique_labels(self, directory):

        labels = self.load_labels(directory)
        
        for l, v in labels.items():
            labels[l] = Munch(v)
        
        labels = Munch(labels)
            
        try:
            labels.main_cat = self.get_unique_labels(labels.prod)
        except Exception:
            labels.main_cat = self.get_unique_labels(labels.ind)

        labels.primary = self.get_unique_labels(labels.primary)
        labels.fin_dem = self.get_unique_labels(labels.fin_dem)
        labels.emis = self.get_unique_labels(labels.emis)
        labels.res = self.get_unique_labels(labels.res)
        labels.mat = self.get_unique_labels(labels.mat)
        labels.car_emis = self.get_unique_labels(labels.car_emis)
        labels.car_res = self.get_unique_labels(labels.car_res)
        labels.car_mat = self.get_unique_labels(labels.car_mat)
        labels.car_prim = self.get_unique_labels(labels.car_prim)

        return(labels)

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

    def get_labels(self, matrix):
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

    def save_labels(self, data, directory):

        try:
            self.get_labels(data["V"].T).to_csv(directory + "industry.csv",
                                                index=False)
        except Exception:
            pass

        self.get_labels(data["Cr_E_k"]).to_csv(directory + "/charact_emissions.csv", index=False)
        self.get_labels(data["Cr_R_k"]).to_csv(directory + "/charact_resources.csv", index=False)
        self.get_labels(data["Cr_M_k"]).to_csv(directory + "/charact_materials.csv", index=False)
        self.get_labels(data["Cr_W_k"]).to_csv(directory + "/charact_factor_inputs.csv", index=False)
        self.get_labels(data["Y"]).to_csv(directory + "/products.csv", index=False)  # with unit column
        self.get_labels(data["Y"].T).to_csv(directory + "/final_demand.csv", index=False)
        try:
            self.get_labels(data["W"]).to_csv(directory + "/factor_inputs.csv", index=False)
            self.get_labels(data["E"]).to_csv(directory + "/emissions.csv", index=False)
            self.get_labels(data["R"]).to_csv(directory + "/resources.csv", index=False)
            self.get_labels(data["M"]).to_csv(directory + "/materials.csv", index=False)
        except Exception:
            self.get_labels(data["w"]).to_csv(directory + "/factor_inputs.csv", index=False)
            self.get_labels(data["e"]).to_csv(directory + "/emissions.csv", index=False)
            self.get_labels(data["r"]).to_csv(directory + "/resources.csv", index=False)
            self.get_labels(data["m"]).to_csv(directory + "/materials.csv", index=False)

    def relabel_to_save(self, data, trans_method, labels_directory):
        """
        This function makes sure that everything is labeled in IOT tables

        trans_method = 0 is prod x prod , 1 is ind x ind
        """
        lb = Munch(self.load_labels(labels_directory))

        if trans_method in [0, 1]:
            cat = lb.prod
        elif trans_method not in [0, 1]:
            cat = lb.ind

        data = Munch(data)

        # Relabel Main IOT elements
        data.Z = self.relabel(data.Z, cat.iloc[:, :4], cat)
        # data.L = relabel(data.L, cat.iloc[:, :4], cat.iloc[:, :4])
        # data.A = relabel(data.A, cat, cat)
        data.Y = self.relabel(data.Y, lb.fin_dem, cat)
        # data.W = relabel(data.W, cat.iloc[:, :4], lb.primary)
        data.w = self.relabel(data.w, cat, lb.primary)

        # Labeling final demand extensions' intensities
        data.Ye = self.relabel(data.Ye, lb.fin_dem, lb.emis)
        data.Yr = self.relabel(data.Yr, lb.fin_dem, lb.res)
        data.Ym = self.relabel(data.Ym, lb.fin_dem, lb.mat)

        # Inter-trans extensions' intensities
        data.e = self.relabel(data.e, cat, lb.emis)
        data.r = self.relabel(data.r, cat, lb.res)
        data.m = self.relabel(data.m, cat, lb.mat)

        # label q
        # data.x = self.relabel(data.x, "x", cat)
        # label balance verification
        # ver_label = "balance (x_out/x_in) - % - 100=balanced - 0=NaN no values"
        # data.ver_base = self.relabel(data.ver_base, ver_label, cat.iloc[:, :4])

        # Relabel Inter-trans extensions
#        data.E = self.relabel(data.E, cat.iloc[:, :4], lb.emis)
#        data.R = self.relabel(data.R, cat.iloc[:, :4], lb.res)
#        data.M = self.relabel(data.M, cat.iloc[:, :4], lb.mat)

        # Relabel characterization tables
        data.Cr_E_k = self.relabel(data.Cr_E_k, lb.emis, lb.car_emis)
        data.Cr_R_k = self.relabel(data.Cr_R_k, lb.res, lb.car_res)
        data.Cr_M_k = self.relabel(data.Cr_M_k, lb.mat, lb.car_mat)
        data.Cr_W_k = self.relabel(data.Cr_W_k, lb.primary, lb.car_prim)

        # Labeling final demand extensions
#        data.YE = self.relabel(data.YE, lb.fin_dem.iloc[:, :4], lb.emis)
#        data.YR = self.relabel(data.YR, lb.fin_dem.iloc[:, :4], lb.res)
#        data.YM = self.relabel(data.YM, lb.fin_dem.iloc[:, :4], lb.mat)

        # Relabel characterized final demand extensions
        # data.Cr_YE = self.relabel(data.Cr_YE, lb.fin_dem, lb.car_emis)
        # data.Cr_YE = self.relabel(data.Cr_YR, lb.fin_dem, lb.car_res)
        # data.Cr_YE = self.relabel(data.Cr_YM, lb.fin_dem, lb.car_mat)

        return(data)

    def apply_labels(self, matrix, labels, axis=0):
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


    def relabel(self, M, column_labels, index_labels):
        """
        Processes apply_labels and apply _names together
        """
        M = df(M)

        try:
            M = self.apply_labels(M, column_labels, axis=1)  # columns
        except Exception:
            # in case a string is passed for column label for a vector
            M.columns = [column_labels]
        M = self.apply_labels(M, index_labels, axis=0)  # index

        return(M)
