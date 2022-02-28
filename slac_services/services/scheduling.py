from prefect import Flow, task, Task
from prefect.engine.results import LocalResult
from prefect.run_configs import KubernetesRun
from prefect.storage import Docker
from prefect.tasks.prefect import create_flow_run, get_task_run_result, wait_for_flow_run
from prefect import Client

from prefect.backend import FlowRunView

import json



class PrefectScheduler:

    def __init__(self):
        self._client = Client()

    def create_project(self, project_name: str):
        self._client.create_project(project_name=project_name)


    def register_flow(self, flow: Flow, project_name: str):
        #flow.run_config = KubernetesRun(
        #    image_pull_policy="Always",
        #    labels=None,
        #)

        flow_id = flow.register(project_name=project_name, build=False)
        return flow_id


    def schedule_flow_run(self, flow_name: str, project_name: str, data: dict = None):
        with Flow("schedule-run") as flow:
            flow_run_id = create_flow_run(
                            flow_name=flow_name,
                            project_name=project_name, 
                            parameters=data
                        )

        flow.run()

        return flow_run_id


    def schedule_and_return_run(self, flow_name: str, project_name: str, data: dict = None):
        with Flow("schedule-run") as flow:
            flow_run_id = create_flow_run(
                            flow_name=flow_name,
                            project_name=project_name, 
                            parameters=data
                        )

            slug = flow.serialize()['tasks'][0]['slug']

            # slug should be absorbed into 
            #child_data = get_task_run_result(flow_run_id, slug)
            #print(child_data)

            res = wait_for_flow_run(flow_run_id)
            #child_data = get_task_run_result(flow_run_id, slug)

        flow_runs = FlowRunView._query_for_flow_run(where={"flow_id": {"_eq": id}})
