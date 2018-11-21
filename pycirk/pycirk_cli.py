# -*- coding: utf-8 -*-
import click
from pycirk import Start


@click.command()
@click.option('--transf_method', '-tm', help='0 = PXP ITA_TC; 1 = PXP ITA_MSC')
@click.option('--directory', '-dr', help='if left black it will be default')
@click.option('--aggregation', '-ag', help='bi-regional (EU-ROW) or None (49 regions)')
@click.option('--make_secondary', '-ms', help='modifies SUT so that secondary materials are apparent in IOT (False or True)')
@click.option('--scenario', '-sc', help='all, 1, 2,... accepted - 0=baseline')
@click.option('--save', '-s', help='0=no, [1-n]=scenario, "all"=save all')
def main(transf_method, directory="", aggregation="bi-regional", make_secondary=False, scenario="all", save=0):
    """
    Console script for pyce. A software to model policy and
    technological interventions in Environmentally Extended Input-Output
    Analysis (EXIOBASE V3.3, 2011)
    """

    a = Start(transf_method, directory, aggregation, make_secondary)
    input("\npress enter to confirm that the scenario is set")

    if scenario == "all":
            s = a.all_results()
    else:
        try:
            s = a.run_one_scenario(scenario)
        except Exception:
            raise ValueError("The value specified for the scenario is invalid")

    if save == "all":
        a.save_everything()
    elif int(save) == 0:
        pass       
    elif int(save) >= 1:
        try:
            a.save_one_scenario(scenario)
        except Exception:
            raise ValueError("The value specified for saving is invalid")

    print(s)


if __name__ == "__main__":
    main()
    
