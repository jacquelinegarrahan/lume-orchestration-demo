# lume-orchestration-demo


Example services...


Spin up servers: ... 
mongodb
prefect



batch not implemented


Instructions (LOCAL):

https://kubernetes.io/docs/tasks/tools/

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

Now, we start the modeling service:

```
kubectl apply -f prefect_deployment.yml
```

```
(prefect-test) PC97901:lume-orchestration-demo jgarra$ kubectl get pods
NAME                                      READY   STATUS      RESTARTS   AGE
model-service-787c79f986-4lfv8            1/1     Running     0          4m56s
prefect-job-1d41e85a-zkrjr                1/1     Running     0          3m25s
prefect-server-agent-85bc5f6cc5-x4jz9     1/1     Running     0          3h17m
prefect-server-apollo-844d6bc99b-q25px    1/1     Running     1          5h34m
prefect-server-create-tenant-job-wqzhl    0/1     Completed   0          5h25m
prefect-server-graphql-5cdd675fdf-2sh87   1/1     Running     0          5h34m
prefect-server-hasura-7997fb8f8c-g2frc    1/1     Running     2          5h34m
prefect-server-postgresql-0               1/1     Running     0          5h34m
prefect-server-towel-7b988d966f-82ngb     1/1     Running     0          5h34m
prefect-server-ui-7c5499bcb6-dtg5n        1/1     Running     0          5h34m
```

# set up port forwardings
```
 kubectl port-forward prefect-server-apollo-844d6bc99b-q25px 4200:4200 & 
 kubectl port-forward prefect-server-ui-7c5499bcb6-dtg5n 8080:8080 &
 kubectl port-forward model-service-787c79f986-4lfv8 5000:5000
```

You can now view the UI at http://localhost:8080.



# TODO
- label assignments