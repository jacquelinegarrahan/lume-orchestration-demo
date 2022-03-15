from numpy import deprecate
from prefect import Flow
from prefect.tasks.prefect import create_flow_run, wait_for_flow_run
from prefect import Client
from prefect.run_configs import KubernetesRun
from prefect.backend import FlowRunView
from prefect.engine.result.base import Result
from prefect.engine.serializers import JSONSerializer
from pydantic import BaseSettings
from pymongo.errors import WriteError
from enum import Enum
import yaml
import json
import hashlib
from typing import List, Any



def fingerprint(**kwargs):

    hasher = hashlib.md5()
    hasher.update({
        json.dumps(kwargs)
    })
    return hasher.hexdigest()


class MongoDBResult(Result):
    # must use ResultDB interface defined in modeling

    def __init__(self, *, results_db, **kwargs):
        kwargs["location"] = fingerprint
        super().__init__(**kwargs)

        self.results_db = results_db


    def exists(self, location: str, **kwargs) -> bool:
        # check whether target result exists

        results = self.results_db.find({"fingerprint": location})

    def read(self, location: str):
        result = self._results_db.get_one()


    def write(self, model_type: str, model_rep: dict, **kwargs):
        # value: doc rep for model
        run_fingerprint = fingerprint(model_rep)
        new = self._copy()
        new.value = model_rep
        new.location = run_fingerprint

        self.logger.debug("Writing result to results database...")

        model_rep.update({"run_fingerprint": run_fingerprint})
       
        # add to mongodb
        insert_result = self.results_db.store_result(model_type, model_rep)

        if insert_result:
            self.logger.debug("Successful write.")

        else:
            raise WriteError("Unable to write to results db.")
            

        return new



class HostMountType(str, Enum):
    # types associated with mounting host filesystem to kubernetes
    # https://kubernetes.io/docs/concepts/storage/volumes/#hostpath
    directory = "Directory"  # directory must exist at given path
    directory_or_create = (
        "DirectorOrCreate"  # if directory does not exist, directory created
    )
    file = "File"  # file must exist at path
    file_or_create = "FileOrCreate"  # will create file if does not exist
    # socket = "Socket" # Unix socket must exist at given path
    # char_device = "CharDevice" # Character device must exist at given path
    # block_device = "BlockDevice" # block device must exist at given path


class MountPoint(BaseSettings):
    name: str
    host_path: str
    mount_type: HostMountType


class KubernetesRunConfig(BaseSettings):
    image_pull_policy: str = "Always"
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
        # mount_points: List[MountPoint] = None,
        build: bool = False,
        #   job_template: str= None,
        #     lume_configuration_file: str=None
    ):
        flow_id = flow.register(project_name=project_name, build=build)

        return flow_id

    def schedule_run(
        self,
        *,
        flow_id: str,
        data: dict = None,
        job_template: str = None,
        mount_points: List[MountPoint] = None,
        lume_configuration_file: str = None,
    ):

        # if no job template provided, pass
        if not job_template and not self._job_template:
            yaml_stream = None

        else:
            yaml_stream = self._load_job_template(
                job_template=job_template,
                mount_points=mount_points,
                lume_configuration_file=lume_configuration_file,
            )

        run_config = self._get_run_config(job_template_rep=yaml_stream)

        flow_run_id = self._client.create_flow_run(
            flow_id=flow_id, parameters=data, run_config=run_config
        )

        return flow_run_id

    def schedule_and_return_run(
        self, *, flow_name: str, project_name: str, data: dict = None
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

    def _load_job_template(
        self,
        *,
        job_template: str = None,
        mount_points: List[MountPoint] = None,
        lume_configuration_file: str = None,
    ):
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


        volumes = []
        container_volume_mounts = []

        if mount_points is not None:
            for mount_point in mount_points:

                volumes.append(
                    {
                        "name": mount_point.name,
                        "hostPath": {
                            "path": mount_point.host_path,
                            "type": mount_point.mount_type.value,
                        },
                    }
                )

                container_volume_mounts.append(
                    {"name": mount_point.name, "mountPath": mount_point.host_path}
                )



        # Using services inside the container will require mounting a configuration file
        # This should probably move to a key/secrets model
        # this will fail the job if not found
        if lume_configuration_file:
            volumes.append(
                {
                    "name": "lume-config",
                    "hostPath": {"path": lume_configuration_file, "type": "File"},
                }
            )

            container_volume_mounts.append(
                {"name": "lume-config", "mountPath": lume_configuration_file}
            )

            #Add var to env
            yaml_stream["spec"]["template"]["spec"]['containers'][0]["env"].append({"name": "LUME_ORCHESTRATION_CONFIG", "value": lume_configuration_file})

        # This assumes only one mounted volume
        yaml_stream["spec"]["template"]["spec"]["volumes"] = volumes
        yaml_stream["spec"]["template"]["spec"]["containers"][0][
            "volumeMounts"
        ] = container_volume_mounts

        return yaml_stream

    def _get_run_config(self, *, job_template_rep: dict):
        # THIS NEEDS TO BE ABSTRACTED SO NOT JUST FOR KUBERNETES
        run_config = KubernetesRun(
            image_pull_policy="Always", job_template=job_template_rep
        )

        return run_config
