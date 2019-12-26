# -*- coding: utf-8 -*-
"""
Created on Tue Feb 7 16:29:23 2017

Description: Organize essential tables for saving

Scope: Modelling the Circular economy in EEIO


@author: Franco Donati
@institution: Leiden University CML
"""


def organizer(data, hybrid):

    if hybrid is True:
    
        return {"Z": data["Z"],
                "Y": data["fd_num"],
                "y_stock_to_waste": data["y_stock_to_waste"],
                "avoided_emiss": data["avoided_emiss_z"],
                "y_crop_res": data["crop_res_y"],
                "z_crop_res": data["crop_res_z"],
                "y_stock_add": data["stock_addition_y"],
                "z_stock_add": data["stock_addition_z"],
                "y_mach_use_waste": data["mach_use_waste_y"],
                "z_mach_use_waste": data["mach_use_waste_z"],
                "y_mach_sup_waste": data["mach_sup_waste_y"],
                "z_mach_sup_waste": data["mach_sup_waste_z"],
                "y_pack_use_waste": data["pack_use_waste_y"],
                "z_pack_use_waste": data["pack_use_waste_z"],
                "y_pack_sup_waste": data["pack_sup_waste_y"],
                "z_pack_sup_waste": data["pack_sup_waste_z"],
                "y_emiss_unreg_w": data["emiss_unreg_w_y"],
                "z_emiss_unreg_w": data["emiss_unreg_w_z"],
                "y_emiss": data["emiss_y"],
                "z_emiss": data["emiss_z"],
                "y_land": data["land_y"],
                "z_land": data["land_z"],
                "z_resource": data["resource_z"],
                "y_resource": data["resource_y"]
                }
        

    else:
        return {"Z": data["Z"],
                "Y": data["Y"],
                "W": data["W"],
                "E": data["E"],
                "R": data["R"],
                "M": data["M"],
                "EY": data["EY"],
                "RY": data["RY"],
                "MY": data["MY"],
                "Cr_E_k": data["Cr_E_k"],
                "Cr_M_k": data["Cr_M_k"],
                "Cr_R_k": data["Cr_R_k"],
                "Cr_W_k": data["Cr_W_k"]
                }