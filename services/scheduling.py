from prefect import Flow, task, Task
from prefect.engine.results import LocalResult
from prefect.run_configs import KubernetesRun
from prefect.storage import Docker

def schedule(func, docker_image):

    def wrapper(*args, **kwargs):

        @task(log_stdout=True)
        def run_fn(*args, **kwargs):
            func(*args, **kwargs)

        flow = Flow(
            func.__name__,
            storage=Docker(
                registry_url="jgarrahan", image_name="my_flow",
                dockerfile="Dockerfile",
                build_kwargs={"nocache": True}
            )
        )

        flow.run_config = KubernetesRun(
            #image="example-env:latest",
            image=docker_image,
            image_pull_policy="Always",
            labels=["example"],
        )


        with flow:
            run_fn(*args, **kwargs)


        flow.run(name='my-test')

    return wrapper

#https://github.com/PrefectHQ/prefect/blob/master/src/prefect/executors/base.py