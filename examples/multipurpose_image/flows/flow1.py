from prefect import Flow, task
from prefect.storage import GitHub
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
    "my-example-flow1",
    storage= GitHub(repo="jacquelinegarrahan/lume-orchestration-demo", path="/examples/multipurpose_image/flows/flow1.py")
    )

with flow:
    extracted_df = extract()
    transformed_df = transform(extracted_df)
    load(transformed_df)
    unrelated = extract()

if __name__ == "__main__":
    create_project("my-example-mp-project")
    register_flow(flow, "my-example-mp-project", image=f"{docker_registry}/lume-orchestration-mp-example:latest")