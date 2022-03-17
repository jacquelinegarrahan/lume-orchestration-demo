from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

from pkg_resources import resource_filename
from pydantic import BaseSettings
import yaml
import os

from slac_services.services.modeling import ModelDBConfig, ModelDB, ResultsMongoDBConfig, ResultsMongoDB, RemoteModelingService, LocalModelingService
from slac_services.services.scheduling import PrefectScheduler
from slac_services.utils import load_yaml_with_env_vars

SDF_RUN_TEMPLATE  = resource_filename(
    "slac_services.files", "kubernetes_job.yaml"
)


# these are hard-coded here, but if abstracted on the laboratory level these would be defined in lab-level package
class SDFModelDBConfig(ModelDBConfig):
    # this needs to be parsed out with new abstracted db
    pool_size= 1

class SDFResultsDBConfig(ResultsMongoDBConfig):
    user: str
    password: str
    host: str
    port: int

class PrefectSchedulerConfig(BaseSettings):
    cluster_mount_point: str

class Settings(BaseSettings):
    model_db_config: SDFModelDBConfig
    results_db_config: SDFResultsDBConfig
    scheduler_config: PrefectSchedulerConfig
    run_template: str = SDF_RUN_TEMPLATE


class SLACServices(containers.DeclarativeContainer):

    config = providers.Configuration()

    model_db = providers.Singleton(
        ModelDB,
        db_uri_template=config.model_db_config.db_uri_template,
        pool_size= config.model_db_config.pool_size,
        user=config.model_db_config.user,
        password=config.model_db_config.password,
        host= config.model_db_config.host,
        port = config.model_db_config.port,
        database=config.model_db_config.database,
    )

    results_db = providers.Singleton(
        ResultsMongoDB,
        db_uri_template=config.results_db_config.db_uri_template,
        host= config.results_db_config.host,
        port = config.results_db_config.port,
        user=config.results_db_config.user,
        password=config.results_db_config.password
    )

    prefect_scheduler = providers.Singleton(
        PrefectScheduler,
        job_template = config.run_template,
        cluster_mount_point = config.scheduler_config.cluster_mount_point,
    )

    remote_modeling_service = providers.Singleton(
        RemoteModelingService,
        model_db=model_db,
        results_db=results_db,
        scheduler=prefect_scheduler
    )

    local_modeling_service = providers.Singleton(
        LocalModelingService,
        model_db=model_db,
    )

    batch_service = ...



def parse_config(filepath):
    """Utility for parsing toml configs
    
    """
    config = load_yaml_with_env_vars(filepath)

    model_db_config = SDFModelDBConfig(**config["model_db"])
    results_db_config = SDFResultsDBConfig(**config["results_db"])
    prefect_scheduler_config = PrefectSchedulerConfig(**config["scheduler"])

    settings = Settings(model_db_config=model_db_config, results_db_config=results_db_config, scheduler_config=prefect_scheduler_config)

    return settings



def initialize_services():
    config_file = os.environ["LUME_ORCHESTRATION_CONFIG"]

    container = SLACServices()
    config = parse_config(config_file)
    container.config.from_pydantic(config)
    return container