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
        self.product_labels = None
        self.industry_labels = None
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
        """
        A general method to calculate the number of unique entries contained
        in a series 
        """
        return len(labels.unique())

    def list_of_something(self, labels):
        """
        A general method to return a list of unique entries contained in a series
        """
        return labels.unique()

    def get_unique_labels(self, dataframe_of_labels, for_units=True):
        """
        Calculates all unique entries (labels) contained in a dataframe and
        puts them together with their units and total count of unique entries
        
        It returns an object... which is munched, not a pretty solution but it
        works ok for now. Please consider refactoring in the future
        """
        organize = dict()

        for keys, labels in dataframe_of_labels.items():
            if for_units is True:
                organize[keys] = self.list_of_something(labels)
            elif for_units is False:
                if keys == "unit":
                    organize[keys] = labels
                else:
                    organize[keys] = self.list_of_something(labels)

        try:
            organize["count"] = len(organize["synonym"])
        except KeyError:
            organize["count"] = len(organize["characterization"])
            
        return Munch(organize)

    def organize_unique_labels(self, directory):

        lbl = self.load_labels(directory)

        self.product_labels = self.get_unique_labels(lbl["prod"])
        try:
            self.industry_labels = self.get_unique_labels(lbl["ind"])
        except AttributeError:
            pass
        
        try:
            self.country_labels = self.product_labels.country_code
        except Exception:
            pass

        self.region_labels = self.product_labels.region

        self.W_labels = self.get_unique_labels(lbl["primary"])
        self.Y_labels = self.get_unique_labels(lbl["fin_dem"])
        self.E_labels = self.get_unique_labels(lbl["emis"], False)
        self.R_labels = self.get_unique_labels(lbl["res"], False)
        self.M_labels = self.get_unique_labels(lbl["mat"], False)
        self.Cr_E_labels = self.get_unique_labels(lbl["car_emis"], False)
        self.Cr_R_labels = self.get_unique_labels(lbl["car_res"], False)
        self.Cr_M_labels = self.get_unique_labels(lbl["car_mat"], False)
        self.Cr_W_labels = self.get_unique_labels(lbl["car_prim"], False)


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

        return {"ind": ind,
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

    def get_labels(self, matrix):
        """
        Collects labels from a dataframe
        """
        try:
            return matrix.index.to_frame(index=False)
            # print("ind",matrix.index[0])
        except Exception:
            # this exception is here only in the case the multi-index is
            # as a list or flat strings instead of an actual multi-index
            # it is not the case with our EXIOBASE database but future 
            #adaptation to include other databases may require it 
            return df(list(matrix.index)).copy()

    def save_labels(self, data, directory):
        """
        saves the labels of the database in the labels directory
        """

        try:
            self.get_labels(data["V"].T).to_csv(directory + "/industry.csv",
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

        try:
            # Relabel Main IOT elements
            data.Z = self.relabel(data.Z, cat.iloc[:, :4], cat)
            data.Y = self.relabel(data.Y, lb.fin_dem, cat)
            data.W = self.relabel(data.W, cat.iloc[:, :4], lb.primary)
        except Exception:
            cat = lb.ind
            prod = lb.prod
            data.V = self.relabel(data.V, cat, prod)

        # Labeling final demand extensions'
        data.EY = self.relabel(data.EY, lb.fin_dem, lb.emis)
        data.RY = self.relabel(data.RY, lb.fin_dem, lb.res)
        data.MY = self.relabel(data.MY, lb.fin_dem, lb.mat)

        # Inter-trans extensions'
        data.E = self.relabel(data.E, cat, lb.emis)
        data.R = self.relabel(data.R, cat, lb.res)
        data.M = self.relabel(data.M, cat, lb.mat)

        # Relabel characterization tables
        data.Cr_E_k = self.relabel(data.Cr_E_k, lb.emis, lb.car_emis)
        data.Cr_R_k = self.relabel(data.Cr_R_k, lb.res, lb.car_res)
        data.Cr_M_k = self.relabel(data.Cr_M_k, lb.mat, lb.car_mat)
        data.Cr_W_k = self.relabel(data.Cr_W_k, lb.primary, lb.car_prim)

        return data

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

        return matrix
               
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
        
        return self.apply_labels(M, index_labels, axis=0)  # index

    def identify_labels(self, M_name):
        """
        A method to understand what type of labels are being handled depending
        on the name of the matrix in dataframe type that is being passed
        """

        # identifying colum and index labels
        if self.country_labels is None:
            reg_labels = self.region_labels
        elif self.country_labels is not None:
            reg_labels = self.country_labels

        if "Y" in M_name:
            column_labels = self.Y_labels
            row_labels = self.product_labels
        else:
            column_labels = self.product_labels
            row_labels = self.product_labels

        if M_name in ["V", "U", "S", "D"]:
            column_labels = self.industry_labels

        name = ""

        if "Cr" in M_name:
            name = "Cr_"
            M_name = M_name[2:]

        if any(True for l in M_name.lower() if l in ["e", "m", "r", "w"]):
            name_2 = [l for l in ["e", "m", "r", "w"] if l in M_name.lower()][0].upper()


            attr_name = name + name_2 + "_labels"
            row_labels = eval("self." + attr_name)
        
        no_row_labs = row_labels.count
        no_reg_labs = len(reg_labels)
        no_col_labs = column_labels.count

        return {"reg_labels": reg_labels,
                "g_labels": column_labels,
                "i_labels": row_labels,
                "no_i": no_row_labs,
                "no_g": no_col_labs,
                "no_reg": no_reg_labs}