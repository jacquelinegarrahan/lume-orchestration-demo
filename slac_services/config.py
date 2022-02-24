from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

from pydantic import BaseSettings
import yaml

from slac_services.modeling import ModelDBConfig, ModelDB, ModelingService, RemoteModelingService, LocalModelingService


class Settings(BaseSettings):
    model_db: ModelDBConfig


class ServiceContainer(containers.DeclarativeContainer):

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
        LocalModelingService
    )


def parse_config(filepath):
    """Utility for parsing toml configs
    
    """
    with open(filepath, 'r') as file:
        config = yaml.safe_load(file)

    model_db = ModelDBConfig(**config["model_db"])

    settings = Settings(model_db=model_db)

    return settings



def initialize_services():
    container = ServiceContainer()
    config = parse_config("config.yml")
    container.config.from_pydantic(config)
    container.init_resources()


if __name__ == "__main__":
    main()