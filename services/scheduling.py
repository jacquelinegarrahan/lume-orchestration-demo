from prefect import Flow, task, Task
from prefect.engine.results import LocalResult
from prefect.run_configs import KubernetesRun



def schedule(func, env={}):

    def wrapper(*args, **kwargs):

        with Flow("example", run_config=KubernetesRun(env=env)) as flow:
            func()

    return wrapper


if __name__ == "__main__":
