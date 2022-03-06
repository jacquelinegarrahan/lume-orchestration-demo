from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

from pydantic import BaseSettings
import yaml
import os

from slac_services.services.modeling import ModelDBConfig, ModelDB, SDFResultsDB, RemoteModelingService, LocalModelingService
from slac_services.services.remote import RemoteEPICSConnectionConfig, RemoteEPICSConnectionService
from slac_services.services.scheduling import PrefectScheduler

# these are hard-coded here, but if abstracted on the laboratory level these would be defined in lab-level package
class LCLSModelDBConfig(ModelDBConfig):
    # this needs to be parsed out with new abstracted db
    db_uri_template="mysql+pymysql://${user}:${password}@127.0.0.1:3306/model_db"
    pool_size= 1

class SDFResultsDBConfig:
    mongo_host="localhost"
    mongo_port=27017

class Settings(BaseSettings):
    model_db: LCLSModelDBConfig
    results_db_config: SDFResultsDBConfig


class SLACServices(containers.DeclarativeContainer):

    config = providers.Configuration()

    model_db = providers.Singleton(
        ModelDB,
        db_uri_template=config.model_db.db_uri_template,
        pool_size= config.model_db.pool_size,
        user=config.model_db.user,
        password=config.model_db.password
    )

    results_db = providers.Singleton(
        SDFResultsDB,
        mongo_host= config.results_db.mongo_host,
        pongo_port = config.results_db.port
    )

    prefect_scheduler = providers.Singleton(
        PrefectScheduler
    )

    remote_modeling_service = providers.Singleton(
        RemoteModelingService,
        model_db=model_db,
        results_db=results_db,
        scheduler = prefect_scheduler
    )

    local_modeling_service = providers.Singleton(
        LocalModelingService,
        model_db=model_db,
    )





def parse_config(filepath):
    """Utility for parsing toml configs
    
    """
    with open(filepath, 'r') as file:
        config = yaml.safe_load(file)

    model_db_config = LCLSModelDBConfig(**config["model_db"])
    results_db_config = SDFResultsDBConfig()

    settings = Settings(model_db=model_db_config, results_db_config=results_db_config)

    return settings



def initialize_services():
    config_file = os.environ["SLAC_CONFIG"]

    container = SLACServices()
    config = parse_config(config_file)
    container.config.from_pydantic(config)
    return container