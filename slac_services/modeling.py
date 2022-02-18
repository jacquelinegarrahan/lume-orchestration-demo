from slac_services.scheduling import schedule_and_return_run


class ModelingService():
    ...

class LocalModelingService(ModelingService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._model_registry = {}

    def infer(self, model_id, input_variables):
        self._model_registry[model_id].evaluate(input_variables)


class RemoteModelingService():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def infer(self, model_id, input_variables):

        data = ...
        flow_name = self._model_registry[model_id]["flow_name"]
        project_name = self._model_registry[model_id]["project_name"]

        schedule_and_return_run(flow_name, project_name, data)
        