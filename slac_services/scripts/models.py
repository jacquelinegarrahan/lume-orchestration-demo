import click
import yaml
import requests
import tempfile
import hashlib
from dependency_injector.wiring import Provide, inject
from slac_services.config import SLACServices
from slac_services.services.modeling import ModelDB, RemoteModelingService
from slac_services.services.scheduling import PrefectScheduler

@click.command()
@click.argument('configuration_file', type=click.File(mode='r'))
@inject
def save_model(configuration_file, model_db: ModelDB = Provide[SLACServices.model_db]):

    config = yaml.safe_load(configuration_file)

    model_id = model_db.save_model(**config["model"])

    click.echo(f"Created model with id: {model_id}")


@click.command()
@click.argument('configuration_file', type=click.File(mode='r'))
@inject
def save_model_deployment(configuration_file, model_db: ModelDB = Provide[SLACServices.model_db]):
    config = yaml.safe_load(configuration_file)


    # get versioned artifact
    response = requests.get(config["model_version"]["url"], stream=True)
    if response.status_code == 200:

        with tempfile.TemporaryFile() as fp:
            fp.write(response.raw.read())
            bytes = fp.read() # read entire file as bytes

            # generate hash for artifact
            readable_hash = hashlib.sha256(bytes).hexdigest()

    config["model_version"]["sha256"] = readable_hash

    model_deployment_id = model_db.save_model_deployment(**config["model_version"])

    click.echo(f"Created model_deployment with id: {model_deployment_id}")


@click.command()
@click.argument('project_name')
@click.argument('description')
@inject
def create_project(project_name, description, model_db: ModelDB = Provide[SLACServices.model_db], scheduling_service: PrefectScheduler = Provide[SLACServices.prefect_scheduler]):
    
    # register flow with prefect
    scheduling_service.create_project(project_name)

    # add project to db
    model_db.create_project(project_name, description)

    click.echo(f"Created project {project_name}")


@click.command()
@click.argument('deployment_id', type=int)
@click.argument('project_name')
@inject
def save_deployment_flow(deployment_id, project_name, remote_modeling_service: RemoteModelingService = Provide[SLACServices.remote_modeling_service]):
    
    flow_id = remote_modeling_service.register_deployment(deployment_id=deployment_id, project_name=project_name)

    click.echo(f"Created project {project_name}")