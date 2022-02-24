from contextlib import contextmanager
from doctest import debug_script
from re import S
from slac_services.scheduling import schedule_and_return_run
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine.base import Connection
from sqlalchemy.exc import OperationalError
from pydantic import BaseSettings
from string import Template



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

    def _execute_sql(self, *args, **kwargs):

        with self.connection as conn:
            # create inspector
            model_cols = self._inspector.get_columns("models")
            col_names = [col["name"] for col in model_cols]
            
            kwarg_string = []
            for kw, value in kwargs.items():

                kwarg_string.append(f"{kw} = {value}")

            sql += kwarg_string.join(" AND ")

            r = conn.execute(sql, *args)

        return r



    def get_model(self, **kwargs):
        sql = """
        SELECT model_id 
        FROM models 
        WHERE 
        """

        return self._execute_sql(sql, **kwargs)


    def save_model(self, *, author, laboratory, facility, beampath, description):
        sql = """
        INSERT INTO models
        (author, laboratory, facility, beampath, description) 
        VALUES (%s, %s, %s, %s, %s)
        """

        return self._execute_sql(sql, author, laboratory, facility, beampath, description)


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

    def get_flow_id(self, deployment_id):
        sql = """
        SELECT flow_id
        FROM flows
        WHERE deployment_id = %s
        """
        return self._execute_sql(sql, deployment_id)



class ModelingService():
    ...


class LocalModelingService(ModelingService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._model_registry = {}

    def get_model(self):
        ...

    def predict(self, model_id, input_variables):
        self._model_registry[model_id].evaluate(input_variables)


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




"""
class ModelSerializationService():
    ...
    # laboratory
    # facility
    # beampath
    # model id

   # EXTRAS
    # author
    # date deployed
    # version
    # metadata
    # flow id 

    # lume-model version -> h5
    # GH artifacts, filesystem 

    def save_my_model(self, mongodb_service, file_store):
        # mongodb_service

    def load_model(model_id) -> LUMEModelObject:
        ...

# LUME-model should use this convention
model.run()
model.output()
"""        
