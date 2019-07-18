# -*- coding: utf-8 -*-
import click
from pycirk import Launch


@click.command()
@click.option('--transf_method', '-tm', default=0, type=int, help='0 = PXP ITA_TC; 1 = PXP ITA_MSC')
@click.option('--save_directory', '-dr', default="", type=str, help='if left black it will be default')
@click.option('--aggregation', '-ag', default=1, type=int, help='1 = bi-regional (EU-ROW) or 0 = None (49 regions)')
@click.option('--make_secondary', '-ms', default=False, type=bool, help='False=no, True=yes - modifies SUT so that secondary materials are apparent in IOT (False or True)')
@click.option('--scenario', '-sc', default=None, type=int, help='all, 1, 2,...')
@click.option('--save_output', '-s', default=False, type=bool, help='False=no, True=yes')
@click.option('--output_dataset', '-od', default=False, type=bool, help='False=no, True=yes')
def main(transf_method, save_directory, aggregation, make_secondary, scenario, save_output, output_dataset):
    """
    Console script for pycirk. A software to model policy and
    technological interventions in Environmentally Extended Input-Output
    Analysis (EXIOBASE V3.3, 2011)
    """
    
    initialize = Launch(transf_method, make_secondary, save_directory, aggregation)
    input("Once you are ready, press enter to continue. It will confirm that scenario.xlsx is ready to be processed")

    click.echo(scenario)
    if scenario is None or scenario is "all":
            output = initialize.all_results()
            if save_output is True:
                initialize.save_results()
    else:
        try:
            output = initialize.scenario_results(scenario)
        except Exception:
            raise ValueError("The value specified for the scenario is invalid")

        if save_output is True:
            try:
                initialize.save_results(scenario, output_dataset)
            except Exception:
                raise ValueError("The value specified for saving is invalid")

    click.echo(output)


if __name__ == "__main__":
    main()
    