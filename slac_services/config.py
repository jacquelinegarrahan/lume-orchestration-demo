from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

from pydantic import BaseSettings
import yaml

from slac_services.services.modeling import ModelDBConfig, ModelDB, ModelingService, RemoteModelingService, LocalModelingService
from slac_services.services.remote import RemoteEPICSConnectionConfig, RemoteEPICSConnectionService


# these are hard-coded here, but if abstracted on the laboratory level these would be defined in lab-level package
class LCLSModelDBConfig(ModelDBConfig):
    db_uri_template="mysql+pymysql://${user}:${password}@127.0.0.1:3306/model_db"
    pool_size= 1

class LCLSProdRemoteEPICSConnectionConfig(RemoteEPICSConnectionConfig):
    host="lcls-prod01.slac.stanford.edu"
    host_port=5086
    local_port=24666
    hop_host="centos7.slac.stanford.edu"

class LCLSDevRemoteEPICSConnection(RemoteEPICSConnectionConfig):
    ...


class Settings(BaseSettings):
    model_db: LCLSModelDBConfig
    lcls_prod_epics_connection: LCLSProdRemoteEPICSConnectionConfig


class SLACServices(containers.DeclarativeContainer):

    config = providers.Configuration()

    model_db = providers.Singleton(
        ModelDB,
        db_uri_template=config.model_db.db_uri_template,
        pool_size= config.model_db.pool_size,
        user=config.model_db.user,
        password=config.model_db.password
    )

    remote_modeling_service = providers.Singleton(
        RemoteModelingService,
        model_db=model_db,
    )

    local_modeling_service = providers.Singleton(
        LocalModelingService,
        model_db=model_db,
    )

    lcls_prod_epics_connection_service = providers.Singleton(
        RemoteEPICSConnectionService,
        host=config.lcls_prod_epics_connection.host,
        user=config.lcls_prod_epics_connection.user,
        password_file=config.lcls_prod_epics_connection.password_file,
        host_port=config.lcls_prod_epics_connection.host_port,
        local_port=config.lcls_prod_epics_connection.local_port,
        hop_host=config.lcls_prod_epics_connection.hop_host,
    )


def parse_config(filepath):
    """Utility for parsing toml configs
    
    """
    with open(filepath, 'r') as file:
        config = yaml.safe_load(file)

    model_db_config = LCLSModelDBConfig(**config["model_db"])
    lcls_prod_epics_config = LCLSProdRemoteEPICSConnectionConfig(**config["lcls_prod_epics"])


    settings = Settings(model_db=model_db_config, lcls_prod_epics_connection=lcls_prod_epics_config)

    return settings



def initialize_services():
    container = SLACServices()
    config = parse_config("config.yml")
    container.config.from_pydantic(config)
    return container