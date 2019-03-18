# -*- coding: utf-8 -*-
"""
Created on Mon Mar 18 17:01:39 2019

@author: donatif
"""

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__