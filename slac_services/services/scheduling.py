from prefect import Flow
from prefect.tasks.prefect import create_flow_run, wait_for_flow_run
from prefect import Client
from prefect.run_configs import KubernetesRun
from prefect.backend import FlowRunView
from pydantic import BaseSettings
from enum import Enum
import yaml
import json
from typing import List


class HostMountType(str, Enum):
    # types associated with mounting host filesystem to kubernetes 
    # https://kubernetes.io/docs/concepts/storage/volumes/#hostpath
    directory = "Directory" # directory must exist at given path
    directory_or_create = "DirectorOrCreate" # if directory does not exist, directory created
    file = "File" # file must exist at path
    file_or_create = "FileOrCreate" # will create file if does not exist
    #socket = "Socket" # Unix socket must exist at given path
    #char_device = "CharDevice" # Character device must exist at given path
    #block_device = "BlockDevice" # block device must exist at given path
    
class MountPoint(BaseSettings):
    name: str
    host_path: str
    mount_type: HostMountType

class KubernetesRunConfig(BaseSettings):
    image_name: str
    image_pull_policy:str="Always"
    job_template: dict

class PrefectScheduler:
    def __init__(self, job_template: str = None, cluster_mount_point: str = None):
        self._client = Client()
        self._job_template = job_template

        # Using cluster mount point here to communicate local cluster mounting...
        # This may differ with
        self._cluster_mount_point = cluster_mount_point

    def create_project(self, project_name: str):
        self._client.create_project(project_name=project_name)

    def register_flow(
        self,
        flow: Flow,
        project_name: str,
        mount_points: List[MountPoint] = None,
        build: bool = False,
        job_template: str= None,
        lume_configuration_file: str=None
    ):

        image_name = f"{flow.storage.registry_url}/{flow.storage.image_name}"
        if flow.storage.image_tag:
            image_name = image_name + f":{flow.storage.image_tag}"


        # if no job template provided, pass
        if not job_template and not self._job_template:
            yaml_stream = None

        else:
            yaml_stream = self._load_job_template(job_template=job_template, mount_points=mount_points, lume_configuration_file=lume_configuration_file)


        # this all needs to be abstracted...
        flow.run_config = self._get_run_config(image_name, yaml_stream)
        flow_id = flow.register(project_name=project_name, build=build)

        return flow_id

    def schedule_run(self, flow_id: str, data: dict = None, job_template: str = None, mount_points: List[MountPoint]=None):
        # SHOULD BE ABLE TO CONFIGURE RUN CONFIG ON A SINGLE RUN AS WELL
        #yaml_stream=self._load_job_template(job_template=job_template, mount_points=mount_points)

        # if job configuration has been changed, need to update the run config on the flow obj
        # if yaml_stream is not None:
        #    run_config = self._get_run_config(yaml_stream)

        with Flow("schedule-run") as flow:

            flow_run_id = create_flow_run(flow_id=flow_id, parameters=data)

        flow.run()

        return flow_run_id

    def schedule_and_return_run(
        self, flow_name: str, project_name: str, data: dict = None
    ):
        # BROKEN
        with Flow("schedule-run") as flow:
            flow_run_id = create_flow_run(
                flow_name=flow_name, project_name=project_name, parameters=data
            )

            slug = flow.serialize()["tasks"][0]["slug"]

            # slug should be absorbed into
            # child_data = get_task_run_result(flow_run_id, slug)
            # print(child_data)

            res = wait_for_flow_run(flow_run_id)
            # child_data = get_task_run_result(flow_run_id, slug)

        flow_runs = FlowRunView._query_for_flow_run(where={"flow_id": {"_eq": id}})


    def _load_job_template(self, job_template: str=None, mount_points: List[MountPoint]=None, lume_configuration_file: str=None):
        if job_template:
            job_template_file = job_template

        elif self._job_template:
            job_template_file = self._job_template
        
        # load job template
        with open(job_template_file, "r") as stream:
            try:
                yaml_stream = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        if mount_points is not None:

            volumes = []
            container_volume_mounts = []

            for mount_point in mount_points:

                volumes.append({
                    "name": mount_point.name,
                    "hostPath": {"path": mount_point.host_path, "type": mount_point.mount_type.value},
                })

                container_volume_mounts.append(
                    {"name":  mount_point.name, "mountPath": mount_point.host_path}
                )

            # Using services inside the container will require mounting a configuration file
            # This should probably move to a key/secrets model
            # this will fail the job if not found
            if lume_configuration_file:
                volumes.append({
                    "name": "lume-config",
                    "hostPath": {"path": lume_configuration_file, "type": "File"},
                })

                container_volume_mounts.append(
                    {"name":  "lume-config", "mountPath": lume_configuration_file}
                )


            # This assumes only one mounted volume
            yaml_stream["spec"]["template"]["spec"]["volumes"] = volumes
            yaml_stream["spec"]["template"]["spec"]["containers"][0]["volumeMounts"] = container_volume_mounts


        return yaml_stream

    def _get_run_config(self, image_name, job_template_rep: dict):
        # THIS NEEDS TO BE ABSTRACTED SO NOT JUST FOR KUBERNETES
        run_config = KubernetesRun(
            image=image_name, image_pull_policy="Always", job_template=job_template_rep
        )

        return run_config