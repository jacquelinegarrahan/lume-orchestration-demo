from contextlib import contextmanager
from doctest import debug_script
from re import S
from unittest.util import strclass
from slac_services.services.scheduling import schedule_and_return_run
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine.base import Connection
from sqlalchemy.exc import OperationalError
from pydantic import BaseSettings, BaseModel
from string import Template
from importlib import metadata, import_module
import subprocess
import sys


class ModelDBConfig(BaseSettings):
    db_uri_template: str
    pool_size: int
    password: str
    user: str


class ModelDB:
    """
    Not safe with mutiprocessing at present
    
    """
    def __init__(self, *, db_uri_template, pool_size, user, password):
        self._db_uri = Template(db_uri_template).substitute(user=user, password=password)
        self._pool_size = pool_size
        self._create_engine()

    def _create_engine(self):
        self._engine = create_engine(self._db_uri, pool_size=self._pool_size)
    
    def _connect(self) -> Connection:
        self._connection = self._engine.connect()
        # update inspector
        self._inspector = inspect(self._engine)
        return self._connection


    @contextmanager
    def connection(self) -> Connection:
        """This is a context manager bc we want to be able to release connection when finished
        """

        # check multiprocessing
        # if pid != pid of current process, create new engine

        # Add cleanup on exit check

        try:
            yield self._connect()

        finally:
            self._connection.close()

    def _execute_sql(self, sql, *args, **kwargs):

        with self.connection() as conn:
            
            kwarg_strings = []
            for kw, value in kwargs.items():

                kwarg_strings.append(f"{kw} = {value}")

            sql += " AND ".join(kwarg_strings)

            r = conn.execute(sql, *args)

        return r

    def get_model(self, **kwargs):
        sql = """
        SELECT model_id 
        FROM models 
        """

        r = self._execute_sql(sql, **kwargs)

        return r

    def save_model(self, *, author, laboratory, facility, beampath, description):
        sql = """
        INSERT INTO models
        (author, laboratory, facility, beampath, description) 
        VALUES (%s, %s, %s, %s, %s)
        """

        r = self._execute_sql(sql, author, laboratory, facility, beampath, description)

        # return inserted id
        return r.lastrowid


    def save_model_deployment(self, *, version, sha256, model_id, url, package_name, asset_dir:str=None, asset_url=None):
        if not asset_dir and not asset_url:
            sql = """
            INSERT INTO model_versions
            (version, sha256, model_id, url, package_name) 
            VALUES (%s, %s, %s, %s, %s)
            """
            args = (version, sha256, model_id, url, package_name)

        elif asset_dir:
            sql = """
            INSERT INTO model_versions
            (version, sha256, model_id, url, asset_dir, package_name) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            args = (version, sha256, model_id, url, asset_dir, package_name)

        elif asset_url:
            sql = """
            INSERT INTO model_versions
            (version, sha256, model_id, url, asset_url, package_name) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            args = (version, sha256, model_id, url)

        r = self._execute_sql(sql, *args)

        # return inserted id
        return r.lastrowid

    def create_project(self, project_name, description):
        sql = """
        INSERT INTO projects
        (project_name, description) 
        VALUES (%s, %s)
        """

        return self._execute_sql(sql, project_name, description)


    def save_flow(self, *, flow_id, deployment_id, flow_name, project_name):
        sql = """
        INSERT INTO flows
        (flow_id, deployment_id, flow_name, project_name) 
        VALUES (%s, %s, %s, %s)
        """

        return self._execute_sql(sql, flow_id, deployment_id, flow_name, project_name)


    def get_latest_deployment(self, model_id):
        sql = """
        SELECT *
        FROM model_versions
        WHERE model_id = %s
        ORDER BY deploy_date DESC
        LIMIT 1
        """

        r = self._execute_sql(sql, model_id)

        return r.first()


    def get_model_flow(self, deployment_id):
        sql = """
        SELECT flow_id
        FROM flows
        WHERE deployment_id = %s
        """
        return self._execute_sql(sql, deployment_id)

    
    def get_latest_model_flow(self, model_id):
        # this is bad sql but rapidly moving and will fix later
        deployment_id = self.get_latest_deployment(model_id).deployment_id


        sql = """
        SELECT flow_id
        FROM flows
        WHERE deployment_id = %s
        """

        r = self._execute_sql(sql, deployment_id)

        return r.scalar()


class ModelingService():

    def __init__(self, *, model_db):
        self._model_db = model_db


class LocalModelingService(ModelingService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._model_registry = {}

    def get_model(self, model_id):

        model = self._model_registry.get(model_id)
        if self._model_registry.get(model_id):
            return model

        else:
            deployment = self._model_db.get_latest_deployment(model_id)

            # try install
            try:
                output = subprocess.check_call([sys.executable, '-m', 'pip', 'install', deployment.url])

            except:
                print(f"Unable to install {deployment.package_name}")
                sys.exit()

            entrypoint_class = metadata.entry_points()['orchestration'][0].value
            module_name, class_name = entrypoint_class.rsplit(":", 1)
            model_class = getattr(import_module(module_name), class_name)
            model =  model_class()

            # add to registry
            self._model_registry[model_id] = model

            return model

    def predict(self, model_id, input_variables):
        return self._model_registry[model_id].evaluate(input_variables)


class RemoteModelingService():
    def __init__(self, model_db: ModelDB, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def predict(self, model_id, input_variables):
        data = ...
        flow_name = self._model_registry[model_id]["flow_name"]
        project_name = self._model_registry[model_id]["project_name"]

        schedule_and_return_run(flow_name, project_name, data)

    def store_results(self, mongo_service):
        ...

    def save_model(self):
        ...

    def load_model(self):
        ...
