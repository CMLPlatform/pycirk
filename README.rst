######
pycirk
######



*A python package to model Circular Economy policy and technological interventions in Environmentally Extended Input-Output Analysis starting from SUTs (EXIOBASE V3.3)*

.. image:: https://zenodo.org/badge/157891556.svg
   :target: https://zenodo.org/badge/latestdoi/157891556
.. image:: https://img.shields.io/badge/License-GPL%20v3-blue.svg
   :target: https://www.gnu.org/licenses/gpl-3.0
.. image:: https://img.shields.io/badge/contributions-welcome-brightgreen.svg
   :target: resources/docs/CONTRIBUTING.md)


| Documentation: https://cmlplatform.github.io/pycirk/

10.5281/zenodo.1492957

===============
1. Installation
===============


1.1. Stable release
-------------------

Run in your terminal:0

	$ pip install pycirk


1.2. From source
----------------

Clone repository:

	$ git clone https://fdonati@bitbucket.org/CML-IE/pycirk.git

Once you have a copy of the source, you can install it with:

    $ python setup.py install

1.3 Data
--------

You can download the biregional or multiregional database by following this link

https://fdonaticml.stackstorage.com/s/OEPbzJQgdIcsAn1

You need to place the data inside the package
e.g. /home/UserName/.local/lib/python3.6/site-packages/pycirk/data

========
2. Usage
========

2.1. Import package
-------------------

	import pycirk


2.2. Initialize
---------------

	my_work = pycirk.Launch(method, directory, aggregation)


2.3. set your scenarios and analysis
------------------------------------

1. Open scenarios.xls in the directory that was specified
2. From there you can specify interventions and parameters for the analysis
3. save and continue to the following steps



2.4. Run scenarios
------------------

Run one specific scenario

    my_work.scenario_results(scen_no, output_dataset)
    (0 = baseline)

Run all scenarios

    my_work.all_results()


2.5. save scenarios
-------------------

Save your results

    my_work.save_results()


2.6. Use from command line

2.6.1. pycirk --help

Usage: pycirk [OPTIONS]

Console script for pycirk. A software to model policy and technological
interventions in Environmentally Extended Input-Output Analysis (EXIOBASE
V3.3, 2011)

Options:

+----------------------------+--------------------------------------+
| Command                    | Variables                            |
+============================+======================================+
|  -tm, --transf_method TEXT | 0 = PXP ITA_TC; 1 = PXP ITA_MSC      |
+----------------------------+--------------------------------------+
|  -dr, --directory TEXT     | if left black it will be default     |
+----------------------------+--------------------------------------+
|  -ag, --aggregation        | 1 = bi-regional (EU-ROW)             |
|                            | 0 = None (49 regions)                |
+----------------------------+--------------------------------------+
|  -sc, --scenario TEXT      | all, 1, 2,... accepted - 0=baseline  |
+----------------------------+--------------------------------------+
|  -s, --save TEXT           | False=no, True=yes                   |
+----------------------------+--------------------------------------+
|  -od, --output_dataset     | False=no, True=yes                   |
+----------------------------+--------------------------------------+
|  --help                    | Show this message and exit.          |
+----------------------------+--------------------------------------+

2.6.2. Command example

    pycirk -tm 0 -dr "" -sc "1" -s True -od False



===========
3. Features
===========


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
- intermediate transactions (Z)
- final demand (Y)
- primary inputs (W)

- emission intermediate extentions (E)
- material intermediate extensions (M)
- resource intermediate extensions (R)
- emission final demand extension (EY)
- material final demand extension (MY)
- resource final demand extensions (RY)

- primary inputs coefficients (w)
- emission intermediate extentions coefficients (e)
- material intermediate extensions coefficients (m)
- resource intermediate extensions coefficients (r)
- emission final demand extension coefficients (eY)
- material final demand extension coefficients (mY)
- resource final demand extensions coefficients (rY)

It is possible to specify:

- region of the intervention
- whether the intervention affects domestic, import transactions or both


====================
4. Important modules
====================

4.1. scenarios.xls
------------------

From this .xls file it is possible to set different types of interventions and the analysis to perform:

- matrix = specifies in which matrix of IOT the changes are applied
- change_type = Primary and ancillary are only used to specify the type of intervention from a conceptual level
- reg_o or reg_d = Regional coordinates (o=origin or row, d=destination or column)
- cat_o or cat_d = category (e.g. products or extensions ) coordinates (o=origin or row, d=destination or column)
- kt = technical coefficient (max achievable technically); a negative value means reduction; unit = %
- ka = absolute values for addition
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



==========
6. Credits
==========

Thanks to dr. Arnold Tukker, dr. Joao Dias Rodriguez for the supervision
dr. Arjan de Koning for knowledge support in exiobase
MSc. Glenn Auguilar Hernandez for testing

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
