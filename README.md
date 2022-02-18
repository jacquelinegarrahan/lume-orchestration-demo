# lume-orchestration-demo


Example services...


Spin up servers: ... 
mongodb
prefect



batch not implemented


# Instructions (LOCAL):


Set up conda environment:
```
conda create -n lume-orchestration-demo python=3.9 prefect cx_Oracle flask lume-model
conda activate lume-orchestration-demo
```

Use [kind](https://kind.sigs.k8s.io/) to create a local cluster:
```
kind create cluster
```

Configure prefect to use backend server:
```
prefect backend server
```

Use [helm](https://helm.sh/) to run prefect services with kubernetes:
```
helm repo add prefecthq https://prefecthq.github.io/server/
helm install prefect-server prefecthq/prefect-server 
```

We use the command `helm update` to apply custom configurations. Mainly, we need to create an agent.

First, autogenerates postgresql password:
```
export POSTGRESQL_PASSWORD=$(kubectl get secret --namespace default prefect-server-postgresql -o jsonpath="{.data.postgresql-password}" | base64 --decode)
```
Now apply changes:
```
helm upgrade \
    prefect-server \
    prefecthq/prefect-server \
    --set postgresql.postgresqlPassword=$POSTGRESQL_PASSWORD \
    --set agent.enabled=true \
    --set jobs.createTenant.enabled=true
```

An agent will be now started on the cluster. To check, get your pods:
```
(prefect-test) PC97901:lume-orchestration-demo jgarra$ kubectl get pods
NAME                                      READY   STATUS      RESTARTS   AGE
prefect-server-apollo-844d6bc99b-dgkfl    1/1     Running     1          2m15s
prefect-server-create-tenant-job-6jtxb    0/1     Completed   3          2m15s
prefect-server-graphql-5cdd675fdf-jj4lk   1/1     Running     0          2m15s
prefect-server-hasura-7997fb8f8c-2xmp2    1/1     Running     2          2m15s
prefect-server-postgresql-0               1/1     Running     0          2m15s
prefect-server-towel-7b988d966f-dqnpx     1/1     Running     0          2m15s
prefect-server-ui-5459c9f645-l964j        1/1     Running     0          2m15s
```

# set up port forwardings
```
 kubectl port-forward prefect-server-apollo-844d6bc99b-q25px 4200:4200 & 
 kubectl port-forward prefect-server-ui-7c5499bcb6-dtg5n 8080:8080 &
 kubectl port-forward model-service-787c79f986-4lfv8 5000:5000
```

You can now view the UI at http://localhost:8080.



# DEMOS

## Custom Dockerfile environment for a flow

```
cd examples/dockerfile_example/flow
```

Set environment variable pointing to DockerHub registry:
```
export DOCKER_REGISTRY={your registry}
```

Now build the Docker image, create the project, and register your flow:
```
python flow.py
```


Now, kick off a flow run:

```
cd ..
python schedule_run.py
```


## Reuse existing docker image for many flows
This is important because it will allow us to create reusable images for different models to be run just by passing configs!

```
cd examples/multipurpose-image/docker
```

Create example image and upload to DockerHub registry

```
docker build -t lume-orchestration-mp-example . 
docker tag lume-orchestration-mp-example <your registry>/lume-orchestration-mp-example
docker push <your registry>/lume-orchestration-mp-example
```

Register flows
```
python examples/multipurpose_image/flows/flow1.py
python examples/multipurpose_image/flows/flow2.py
python examples/multipurpose_image/flows/flow3.py
```

Now, lets kick them off:
```
python examples/multipurpose_image/schedule_run.py
```





# TODO
- label assignments
- Create flow runs using GH actions on releases