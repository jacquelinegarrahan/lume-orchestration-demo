from prefect import Flow, task
from prefect.storage import Docker
import time
import pandas as pd
from slac_services.scheduling import create_project, register_flow
import os
import sys


# Requires a docker registry
docker_registry = os.environ.get("DOCKER_REGISTRY")
if not docker_registry:
    print("Requires docker registry to be set.")
    sys.exit()


@task(log_stdout=True)
def extract():
    """ Return dummy result"""
    time.sleep(20)
    return pd.DataFrame({"example-df": [0, 1, 2, 4]})


@task(log_stdout=True)
def transform(x):
    """ Return dummy result """
    time.sleep(20)
    return x


@task(log_stdout=True)
def load(y):
    time.sleep(20)
    print(f"Finished, {y}")


flow = Flow(
    "my-example-flow",
    storage=Docker(registry_url=docker_registry, image_name="my-example-flow",
    dockerfile="Dockerfile",
    build_kwargs={"nocache": True}
    )
)

with flow:
    extracted_df = extract()
    transformed_df = transform(extracted_df)
    load(transformed_df)
    unrelated = extract()

if __name__ == "__main__":
    create_project("my-example-project")
    register_flow(flow, "my-example-project")