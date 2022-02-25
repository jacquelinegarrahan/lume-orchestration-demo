import click
import yaml
from dependency_injector.wiring import Provide, inject
from slac_services import SLACServices
from slac_services.services.modeling import ModelDB

@click.command()
@click.argument('configuration_file', type=click.File(mode='r'))
@inject
def save_model(configuration_file, model_db: ModelDB = Provide[SLACServices.model_db]):

    config = yaml.safe_load(configuration_file)

    model_id = model_db.save_model(**config["model"])

    click.echo(f"Created model with id: {model_id}")


@click.command()
@click.argument('configuration_file', type=click.File(mode='r'))
def save_model_deployment():
    """Example script."""
    config = yaml.safe_load(configuration_file)

    click.echo('Hello World!')