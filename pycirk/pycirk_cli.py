# -*- coding: utf-8 -*-
import click
from pycirk import Launch


@click.command()
@click.option('--transf_method', '-tm', help='0 = PXP ITA_TC; 1 = PXP ITA_MSC')
@click.option('--save_directory', '-dr', help='if left black it will be default')
@click.option('--aggregation', '-ag', help='1 = bi-regional (EU-ROW) or 0 = None (49 regions)')
@click.option('--make_secondary', '-ms', help='False=no, True=yes - modifies SUT so that secondary materials are apparent in IOT (False or True)')
@click.option('--scenario', '-sc', help='all, 1, 2,...')
@click.option('--save_directory', '-s', help='False=no, True=yes')
@click.option('--output_dataset', '-od', help='False=no, True=yes')
def main(transf_method, save_directory=None, aggregation=None, make_secondary=False, scenario="all", output_dataset=False):
    """
    Console script for pycirk. A software to model policy and
    technological interventions in Environmentally Extended Input-Output
    Analysis (EXIOBASE V3.3, 2011)
    """
    if aggregation is None:
        aggregation = 1
    else:                
        try:
            aggregation = int(aggregation)
        except Exception:
            pass

    initialize = Launch(transf_method, make_secondary, save_directory, aggregation)
    input("\npress enter to confirm that the scenario is set")


    if scenario == "all":
            output = initialize.all_results()
            if save_directory is True:
                initialize.save_results()
    else:
        try:
            output = initialize.scenario_results(scenario)
        except Exception:
            raise ValueError("The value specified for the scenario is invalid")

        if save_directory is True:
            try:
                initialize.save_results(scenario, output_dataset)
            except Exception:
                raise ValueError("The value specified for saving is invalid")

    print(output)


if __name__ == "__main__":
    main()
