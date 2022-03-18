from contextlib import contextmanager
from doctest import debug_script
from re import S
from unittest.util import strclass
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine.base import Connection
from pydantic import BaseSettings
from string import Template
from importlib import import_module
from slac_services.services.scheduling import PrefectScheduler
from slac_services.utils import flatten_dict
import subprocess
import sys
from importlib_metadata import distribution
from pymongo import MongoClient
import pandas as pd 
from abc import ABC, abstractmethod
from typing import List

class ModelDBConfig(BaseSettings):
    db_uri_template: str= "mysql+pymysql://${user}:${password}@${host}:${port}/${database}"
    pool_size: int
    password: str
    user: str
    host: str
    port: int
    database: str


class ModelDB:
    """
    Not safe with mutiprocessing at present

    This needs to be separated into model database and mysql implementation of database
    
    """
    def __init__(self, *, db_uri_template, pool_size, user, password, host, port, database):
        self._db_uri = Template(db_uri_template).substitute(user=user, password=password, host=host, port=str(port), database=database)
        self._pool_size = pool_size
        self._connection = None
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
            if self._connection is not None:
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

    def get_deployment(self, deployment_id):
        sql = """
        SELECT *
        FROM model_versions
        WHERE deployment_id = %s
        ORDER BY deploy_date DESC
        LIMIT 1
        """

        r = self._execute_sql(sql, deployment_id)

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


    def store_flow(self, *, flow_id, deployment_ids: List[int], flow_name, project_name):
        sql = """
        INSERT INTO flows
        (flow_id, deployment_id, flow_name, project_name) 
        VALUES (%s, %s, %s, %s)
        """

        for deployment_id in deployment_ids:
            self._execute_sql(sql, flow_id, deployment_id, flow_name, project_name)

        return True
    

class ResultsDB(ABC):

    @abstractmethod
    def __init__(self):
        ...
    
    @abstractmethod
    def find(self):
        ...

    @abstractmethod
    def store(self):
        ...


class ResultsMongoDBConfig(BaseSettings):
    db_uri_template: str = "mongodb://${user}:${password}@${host}:${port}"
    password: str
    user: str
    host: str
    port: int


class ResultsMongoDB(ResultsDB):

    # Note: pymongo is threadsafe

    def __init__(self, *, db_uri_template, user, password, host, port):

        # need to transition off of plaintext templating
        self._db_uri = Template(db_uri_template).substitute(user=user, password=password, host=host, port=str(port))
        self._client = MongoClient(self._db_uri)
        self._db = self._client.model_results

    def store(self, *, model_type, model_rep) -> bool:
        insert_result = self._client.model_results[model_type].insert_one(model_rep)
        
        if insert_result.inserted_id:
            return True
        
        else:
            return False

    def find(self, *, model_type, query={}, fields={}) -> pd.DataFrame:
        results = self._db[model_type].find((query, fields))
        
        return list(results)

    def find_all(self, *, model_type):
        results = self._db[model_type].find()
        return list(results)

    def load_dataframe(self, *, model_type, query={}, fields={}):
        # flattens results and returns dataframe
        results = list(self._db[model_type].find((query, fields)))
        flattened = [flatten_dict(res) for res in results]
        df = pd.DataFrame(flattened)

        # Load DataFrame
        df["date"] = pd.to_datetime(df["isotime"])
        df["_id"] = df["_id"].astype(str)

        return df


    

class ModelingService():

    def __init__(self, *, model_db):
        self._model_db = model_db
        self._model_registry = {}

    def _install_deployment(self, deployment):
        # get remote tarball
        # conda instead of pip
        # get requirements from environment.yml

        raw_url = deployment.url.replace("github", "raw.githubusercontent")
        raw_url = raw_url.replace("tree/", "")

        # assumes using environment yaml and main branch
        raw_url = f"{raw_url}/environment.yml"

        # try install
        try:
         #   output = subprocess.check_call([sys.executable, '-m', 'pip', 'install', deployment.url])
            output = subprocess.check_call(["conda", "env", "update", "--file", raw_url])

        except:
            print(f"Unable to install environment for {deployment.package_name}")
            sys.exit()


        # try install of package 
        try:
            output = subprocess.check_call([sys.executable, '-m', 'pip', 'install', f"git+{deployment.url}"])
         #   output = subprocess.check_call(["conda", "env", "update", "--file", raw_url])

        except:
            print(f"Unable to install {deployment.package_name}")
            sys.exit()
 
        dist = distribution(deployment.package_name)
        model_entrypoint = dist.entry_points.select(group="orchestration", name=f"{deployment.package_name}.model")
        if len(model_entrypoint):
            model_entrypoint = model_entrypoint[0].value

        flow_entrypoint = dist.entry_points.select(group="orchestration", name=f"{deployment.package_name}.flow")
        if len(flow_entrypoint):
            flow_entrypoint = flow_entrypoint[0].value

        # add to registry
        self._model_registry[deployment.model_id] = {"model_entrypoint": model_entrypoint, "package": deployment.package_name, "flow_entrypoint": flow_entrypoint}


class LocalModelingService(ModelingService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def get_model(self, model_id: int):
        # add function to get old deployment

        if self._model_registry.get(model_id) is not None:
            pass

        else:
            deployment = self._model_db.get_latest_deployment(model_id)
            self._install_deployment(deployment)

        return self._load_model_from_entrypoint(self._model_registry[model_id]["model_entrypoint"])

    def predict(self, *, model_id: int, input_variables):
        model = self.get_model(model_id)

        return model.evaluate(input_variables)

    @staticmethod
    def _load_model_from_entrypoint(model_entrypoint):
        module_name, class_name = model_entrypoint.rsplit(":", 1)
        model_class = getattr(import_module(module_name), class_name)

        return model_class()


class RemoteModelingService(ModelingService):
    def __init__(self, scheduler: PrefectScheduler, results_db: ResultsDB, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._scheduler = scheduler
        self._results_db = results_db

    def predict(self, *, model_id, data, mount_points=None, lume_configuration_file=None):

        #only using latest for now
        flow_id = self._model_db.get_latest_model_flow(model_id)
        self._scheduler.schedule_run(flow_id=flow_id, data=data, mount_points=mount_points, lume_configuration_file=lume_configuration_file)


    def register_deployment(self, *, deployment_id, project_name):
        deployment = self._model_db.get_deployment(deployment_id)
        self._install_deployment(deployment)
        #register_flow(self, flow: Flow, project_name: str, image: str = None):

        flow_entrypoint = self._model_registry[deployment.model_id]["flow_entrypoint"]
        flow = self._return_flow_from_entrypoint(flow_entrypoint)

        flow_id = self._scheduler.register_flow(flow, project_name)

        self._model_db.store_flow(flow_id =flow_id, deployment_ids=[deployment_id],flow_name= self._model_registry[deployment.model_id]["package"], project_name=project_name)

        return flow_id


    @staticmethod
    def _return_flow_from_entrypoint(flow_entrypoint):

        module_name, fn_name = flow_entrypoint.rsplit(":", 1)
        fn = getattr(import_module(module_name), fn_name)

        return fn()

    def save_model(self):
        ...

    def load_model(self):
        ...
