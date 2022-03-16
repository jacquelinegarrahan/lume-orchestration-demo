# lume-orchestration-demo


# Instructions (LOCAL):


Set up conda environment:
```
conda create -n lume-orchestration-demo python=3.9 prefect cx_Oracle flask lume-model
conda activate lume-orchestration-demo
```

Use [kind](https://kind.sigs.k8s.io/) to create a local cluster. First, create a file `kind-config.yaml` with the following information:
```
apiVersion: kind.x-k8s.io/v1alpha4
kind: Cluster
nodes:
  - role: control-plane
    extraMounts:
      - hostPath: <PATH_TO_LUME_ORCHESTRATION_DEMO>
        containerPath: <PATH_TO_LUME_ORCHESTRATION_DEMO>
```

Next, create your cluster:
```
kind create cluster --config=kind-config.yaml
```

Configure prefect to use backend server:
```
prefect backend server
```

Use [helm](https://helm.sh/) to run prefect services with kubernetes:
```
helm repo add prefecthq https://prefecthq.github.io/server/
helm install prefect-server prefecthq/prefect-server -f prefect/prefect.yaml
```

 To check, get your cluster:
```
(prefect-test) PC97901:lume-orchestration-demo jgarra$ kubectl get pods
NAME                                      READY   STATUS      RESTARTS   AGE
prefect-server-apollo-844d6bc99b-dgkfl    1/1     Running     1          2m15s
prefect-server-agent-85bc5f6cc5-g5gr6     1/1     Running     3          73s
prefect-server-create-tenant-job-6jtxb    0/1     Completed   3          2m15s
prefect-server-graphql-5cdd675fdf-jj4lk   1/1     Running     0          2m15s
prefect-server-hasura-7997fb8f8c-2xmp2    1/1     Running     2          2m15s
prefect-server-postgresql-0               1/1     Running     0          2m15s
prefect-server-towel-7b988d966f-dqnpx     1/1     Running     0          2m15s
prefect-server-ui-5459c9f645-l964j        1/1     Running     0          2m15s
```

Now create mysql db (8.0.28):
```
helm install model-db bitnami/mysql -f model_db/values.yaml
```
```
(lume-orchestration-demo) PC97901:lume-orchestration-demo jgarra$ kubectl get pods
NAME                                      READY   STATUS      RESTARTS   AGE
model-db-mysql-0                          1/1     Running     0          48m
```

Set up results database:
```
helm install results-db bitnami/mongodb -f results_db/values.yaml
```

# install impact dashboard chart

```
helm install impact-dashboard impact-dashboard -f impact-dashboard/values.yaml --set dashboard_hostdir=$DASHBOARD_DIR
```

# set up port forwardings ( can alternatively look up pod name via kubectl get pods)
```
 kubectl port-forward $(kubectl get pods | grep prefect-server-apollo | awk '{n=split($2,b," "); print $1}') 4200:4200 & 
 kubectl port-forward $(kubectl get pods | grep prefect-server-ui | awk '{n=split($2,b," "); print $1}') 8080:8080 &
 kubectl port-forward $(kubectl get pods | grep results-db | awk '{n=split($2,b," "); print $1}') 27017:27017 &
 kubectl port-forward model-db-mysql-0 3306:3306 
```

You can now view the UI at http://localhost:8080.

# Apply model db schema
Log in to mysql:

```
mysql -u root -h 127.0.0.1 -ppassword
source model_db/schema.sql
```



# DEMOS

```
export LUME_ORCHESTRATION_CLUSTER_CONFIG=$(pwd)/examples/cluster-config.yaml
export LUME_ORCHESTRATION_CONFIG=$(pwd)/examples/config.yaml
```

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




## Use EPICS service to get current values

## Run locally

## Defining flow
The GitHub action creating the flow image is here: add link

This requires the definition of repository secrets DOCKER_USERNAME and DOCKER_PASSWORD



## Dev notes:

Using dependency injection and inversion of control

- Break into lume-services/SLAC services
- Move templated projects for repositories
- Completed config.yaml with all networking configs +
- Impact -> archive and package with +
- Bmad -> tao.in, lat.bmad
- Result storage + 
- Volume mounting +
- High level flow & composite flow tracking +
- Eventually link with dashboard demo
    - mongodb service +
- private repository
- Uniqueness constraints
