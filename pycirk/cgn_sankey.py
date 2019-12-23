# -*- coding: utf-8 -*-
"""
CG Sankey diagram

It returns Sankey diagram for the global input-output material flows
from 'cg_world' dataframe in 'code.py'

Note: Run function in Jupyter Notebook for better performance of
SankeyWidgeand  visualization

Created on Fri Sep 28 13:35:25 2018

Updated on Mon Oct 29 10:43:00 2018

@author: aguilarga
"""
import pandas as pd
import floweaver as fw
from ipysankeywidget import SankeyWidge


def sankey_fw(frame):
    # FLOWS FOR USING FLOWEAVER
    df = frame.sum(1)
    flows = pd.DataFrame([['N', 'P', 'fossil', df[0]],
                          ['N', 'P', 'biomass', df[1]],
                          ['N', 'P', 'metal', df[2]],
                          ['N', 'P', 'nonmetal', df[3]],
                          ['P', 'E', 'fossil', df[4]],
                          ['P', 'E', 'biomass', df[5]],
                          ['P', 'E', 'metal', df[6]],
                          ['P', 'E', 'nonmetal', df[7]],
                          ['P', 'W', 'fossil', df[8]],
                          ['P', 'W', 'biomass', df[9]],
                          ['P', 'W', 'metal', df[10]],
                          ['P', 'W', 'nonmetal', df[11]],
                          ['P', 'S', 'fossil', df[12]],
                          ['P', 'S', 'biomass', df[13]],
                          ['P', 'S', 'metal', df[14]],
                          ['P', 'S', 'nonmetal', df[15]],
                          ['S', 'W', 'fossil', df[16]],
                          ['S', 'W', 'biomass', df[17]],
                          ['S', 'W', 'metal', df[18]],
                          ['S', 'W', 'nonmetal', df[19]],
                          ['W', 'G', 'fossil', df[20]],
                          ['W', 'G', 'biomass', df[21]],
                          ['W', 'G', 'metal', df[22]],
                          ['W', 'G', 'nonmetal', df[23]],
                          ['W', 'P', 'fossil', df[24]],
                          ['W', 'P', 'biomass', df[25]],
                          ['W', 'P', 'metal', df[26]],
                          ['W', 'P', 'nonmetal', df[27]]])
    flows.columns = ['source', 'target', 'type',	 'value']
    # SETTINS
    size = dict(width=750, height=300)
    nodes = {'N': fw.ProcessGroup(['N']),
             'I&C': fw.ProcessGroup(['C']),
             'S': fw.ProcessGroup(['S']),
             'W': fw.ProcessGroup(['W']),
             'DPO': fw.ProcessGroup(['E', 'G']),
             'rec': fw.Waypoint(direction='L'), }
    ordering = [[['N'], []],
                [['I&C'], ['rec']],
                [['S'], []],
                [['W'], []],
                [['DPO'], []]]
    bundles = [fw.Bundle('N', 'I&C'),
               fw.Bundle('I&C', 'W'),
               fw.Bundle('I&C', 'S'),
               fw.Bundle('I&C', 'DPO'),
               fw.Bundle('S', 'W'),
               fw.Bundle('W', 'DPO'),
               fw.Bundle('W', 'I&C'), ]
    sdd = fw.SankeyDefinition(nodes, bundles, ordering)
    out_by_name = fw.Partition.Simple('process', ['E', 'G'])
    nodes['DPO'].partition = out_by_name
    flow_by_type = fw.Partition.Simple('type',
                                       ['fossil', 'biomass',
                                        'metal', 'nonmetal'])
    palette = {'fossil': 'yellow', 'biomass': 'green',
               'metal': 'blue', 'nonmetal': 'orange'}
    sdd = fw.SankeyDefinition(nodes, bundles, ordering,
                              flow_partition=flow_by_type)
    fw.weave(sdd, flows, palette=palette).to_widget(**size)
    return flows
