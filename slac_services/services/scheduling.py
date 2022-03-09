from prefect import Flow
from prefect.tasks.prefect import create_flow_run, wait_for_flow_run
from prefect import Client
from prefect.run_configs import KubernetesRun
from prefect.backend import FlowRunView
import yaml
import json


class SDFRunConfig:
    ...


class PrefectScheduler:

    def __init__(self, job_template: str = None, cluster_mount_point: str=None):
        self._client = Client()
        self._job_template = job_template

        # Using cluster mount point here to communicate local cluster mounting...
        # This may differ with 
        self._cluster_mount_point = cluster_mount_point

    def create_project(self, project_name: str):
        self._client.create_project(project_name=project_name)


    def register_flow(self, flow: Flow, project_name: str, mount_point: str=None, build: bool = False):

        image_name = f"{flow.storage.registry_url}/{flow.storage.image_name}"
        if flow.storage.image_tag:
            image_name = image_name + f":{flow.storage.image_tag}"

        # load job template
        if self._job_template:
            with open(self._job_template, "r") as stream:
                try:
                    yaml_stream = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    print(exc)

            # if mount point also given, modify yaml
            # This assumes only one mounted volume
            yaml_stream["spec"]["template"]["spec"]["volumes"] = [
                {'name': 'filesystem-dir', 'hostPath': {'path': mount_point, 'type': 'Directory'}}
            ]

            yaml_stream["spec"]["template"]["spec"]["containers"][0]["volumeMounts"] =  [{'name': 'filesystem-dir', 'mountPath': mount_path}]

            
        # this all needs to be abstracted... 
        flow.run_config = KubernetesRun(image=image_name, image_pull_policy="Always", job_template=yaml_stream)

        flow_id = flow.register(project_name=project_name, build=build)

        return flow_id


    def schedule_run(self, flow_id: str, data: dict = None):
        with Flow("schedule-run") as flow:
            flow_run_id = create_flow_run(
                            flow_id=flow_id,
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
