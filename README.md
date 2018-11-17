# pyce

_A software to model Circular Economy policy and technological interventions in Environmentally Extended Input-Output Analysis starting from SUTs (EXIOBASE V3.3)_

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](resources/docs/CONTRIBUTING.md)

Documentation: https://bitbucket.org/CML-IE/pyce/src/master/

## Installation

### Stable release

Run in your terminal:

	$ pip install pyce # currently not uploaded to PyPI. It will be there by the end of July 20148 

### From source

Clone repository:

	$ git clone https://fdonati@bitbucket.org/CML-IE/pyce.git
or

	$ git clone https://github.com/CMLPlatform/pyce.git


Once you have a copy of the source, you can install it with:
	
    $ python setup.py install


## Usage

### Import package

	import pyce

### Initialize
    
    s = pyce.Start(method, directory, aggregation, make_secondary)

### set your scenarios and analysis 

1. Open scenarios.xls in the directory that was specified
2. From there you can specify interventions and parameters for the analysis
3. save and continue to the following steps

### Run scenarios

Run one specific scenario

    s.run_one_scenario(scen_no, results_only=[False, True]) 
    (0 = baseline)


Run all scenarios

    s.all_results()

### save scenarios

Save one specific scenario

    s.save_one_scenario(scen_no, results_only=[False, True])

Save the summary of your results 
    
    s.save_results() 

Save your entire project

    s.save_everything()
    

### Use from command line

pyce --help

Usage: pyce [OPTIONS]

Console script for pyce. A software to model policy and technological
interventions in Environmentally Extended Input-Output Analysis (EXIOBASE
V3.3, 2011)
    
Options:

| Command                    | Variables                            |
|----------------------------|--------------------------------------|
|  -tm, --transf_method TEXT | 0 = PXP ITA_TC; 1 = PXP ITA_MSC      |
|  -dr, --directory TEXT     | if left black it will be default     |
|  -sc, --scenario TEXT      | all, 1, 2,... accepted - 0=baseline  |
|  -s, --save TEXT           | 0=no, [1-n]=scenario, "all"=save all |
|  --help                    | Show this message and exit.          |


Command example

    pyce -tm 0 -dr "" -sc "all" -s "all"




## Features

Examples of policies that can be modelled through the software:

- sharing
- recycling
- life extension
- rebound effects
- substituion
- market and value added changes
- efficiency

The tables in which it is possible to apply changes:

- total requirement matrix (A)
- intermediate transactions (S)
- final demand (Y)
- primary inputs coefficients (RE)
- emission intermediate extentions coefficients (RBe)
- material intermediate extensions coefficients (RBm)
- resource intermediate extensions coefficients (RBr)
- emission final demand extension coefficients (RYBe)
- material final demand extension coefficients (RYBm)

It is possible to specify:

- region of the intervention
- whether the intervention affects domestic, import transactions or both



## Important modules


### pyce.py

1. Initiates the operations to set scenarios and to create IOT from SUT based on prodxprod Industry-Technology assumption both under Market Share Coefficient method and Technical Coefficient method.
2. From start you can launch all the analysis specifications listed under scenarios.xls and save everything
3. Results will be saved in the output folder

Permitted SUT transformation Methods:

- method = 0 >> Prod X Prod Ind-Tech Assumption Technical Coeff method
- method = 1 >> Prod X Prod Ind-Tech Assumption Market Share Coeff method
- results_only = True >> output only results (spec'd in scenarios.xls under analysis)
- results_only = False >> output all IOTs and results
- scen_no = 0 - n (0 = baseline) 
- n = is number of scenarios specified by sheet in scenarios.xls
- "scenario_1" is also allowed for scenarios
- None, 0, base and baseline are also accepted for baseline
- aggregation = ["", "bi-regional"](bi-regional EU-ROW), None (Multi-regional 49 countries) 


### scenarios.xls

From this .xls file it is possible to set different types of interventions and the analysis to perform:

- matrix = specifies in which matrix of IOT the changes are applied
- intervention = Primary and ancillary are only used to specify the type of intervention from a conceptual level
- reg_o or reg_d = Regional coordinates (o=origin or row, d=destination or column)
- cat_o  or cat_d = category (e.g. products or extensions ) coordinates (o=origin or row, d=destination or column)
- kt = technical coefficient (max achievable technically); a negative value means reduction; unit = %
- kp = penetration coefficient (level of market penetration of the policy); unit = %
- copy = allows you to copy a specific transation to a different point in the matrices (useful for proxy creation)
- substitution = tells the software whether it needs to substitute values among specified categories
- sk = which intervention should be substituted
- swk = Substitution weighing factor (how much of the original transaction should be substituted); allows to simulate difference in prices and physical properties between categories; unit = %

These can be set for:

- product category e.g. C_STEL (basic iron), C_PULP (pulp), etc.
- final demand category e.g. F_HOUS (households), F_GOVE (government), etc.
- primary input category e.g. E_HRHS (employment highly skilled), T_TLSA (taxes less subsidies), etc.
- emissions extensions e.g. E_CO2_c (CO2 - combustion)
- material extensions e.g. NI.02 (Nature Inputs: Coking Coal)
- resource extension e.g. L_1.1 (Land use - Arable Land - Rice)

Furthemore, from the analysis sheet you can set the following variables to be compared in the analysis:

- product categories
- primary input categories
- emissions extensions
- material extensions
- resource extensions
- region of interest
- impact categories # Please see the data_validation_list sheet in the scenarios.xls file for the comprehensive list

### make_secondary.py
Allows for the modification of secondary material flows in the SUTs so that they are visible in the IO system


## Other modules

### results.py

Class to assemble results for analysis as specified in scenario.xls analysis sheet:

- Output product content in other products
- Output results for each scenario
- Output results and all IO tables and extensions 


### save_.py

Save class:

- Save one scenario results
- Save one scenario results + IOTs
- Save all scenarios + IOTs
- Save all results


### apply_policy.py

Policy interventions class:

- Recreate any matrix in IOT from policy interventions listed in the scenarios scenarios.xls

### base_n_scen.py

Calculate IOT for baseline and scenarios from SUTs


### SUTtoIOT.py

Assemblying IOTs and Extensions from: 

- Prod x prod industry technology assumption in market share coefficient method
- Prod x prod industry technology assumption in technical coefficient method


### SUTops.py

Class for fundamental mathematical operations of IOA and SUT


### labels.py 

General labels for tables	



## Credits

Thanks to dr. Arnold Tukker, dr. Joao Dias Rodriguez for the supervision 
dr. Arjan de Koning for knowledge support in exiobase
MSc. Glenn Auguilar Hernandez for testing

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
