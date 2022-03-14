from prefect import Flow, task
from prefect.storage import Docker
import time
import pandas as pd
import os
import sys


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
    print(y)
    return y


flow = Flow(
    "my-example-flow",
    storage=Docker(registry_url="jgarrahan", image_name="my-example-flow",
    dockerfile="Dockerfile",
    build_kwargs={"nocache": True},
    stored_as_script=True,
    path=f"/opt/prefect/flow.py",
    image_tag="latest"
    )
)

with flow:
    extracted_df = extract()
    transformed_df = transform(extracted_df)
    load(transformed_df)
    unrelated = extract()

if __name__ == "__main__":
    from slac_services import service_container
    scheduler = service_container.prefect_scheduler()

    flow_id = scheduler.register_flow(flow, "examples", build=True)
    