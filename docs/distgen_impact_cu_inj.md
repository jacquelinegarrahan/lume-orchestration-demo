# Demo:

A distgen -> impact model of the copper injector has been packaged for compatability with the LUME/SLAC services [here](https://github.com/jacquelinegarrahan/distgen-impact-cu-inj-ex).

Add the distgen model to the model database using the description packaged at `examples/distgen_impact_cu_inj/distgen_impact_cu_inj.yaml`.
```
save-model examples/distgen_impact_cu_inj/distgen_impact_cu_inj.yaml
```
The command with output a model id associated with the saved model. Export this value to the environment variable `DISTGEN_IMPACT_CU_INJ_MODEL_ID`:

```
export DISTGEN_IMPACT_CU_INJ_MODEL_ID={save-model output model ID}
```

You can check the model entry in the database directly by logging into mysql to check the model has been saved:
```
mysql -u root -h 127.0.0.1 -ppassword
use model_db
select * from models;
```

Now, create an entry for the versioned deployment:
```
save-model-deployment examples/distgen_impact_cu_inj/deployment.yaml
```
Save this deployment id to an environment variable:
```
export DISTGEN_IMPACT_CU_INJ_DEPLOYMENT_ID={save-model-deployment output deployment ID}
```

You can check this has been tracked in the database:
```
mysql -u root -h 127.0.0.1 -ppassword
use model_db
select * from model_versions
```

## Register with remote modeling service

In order to use the remote modeling service, we must register a flow associated with the deployment with Prefect. Prefect flows are organized into projects.

Create a project `my-models` for use with these demos. If this has already been created, pymysql will raise an error, which is fine and can be ignored for now.:

```
create-project my-models "test model creation"
```

We can now register a flow associated with our deployment id to this project:

```
save-deployment-flow $DISTGEN_IMPACT_CU_INJ_DEPLOYMENT_ID my-models
```


## Open notebook

Continue the demo in the Jupyter notebook included in `examples/distgen_impact_cu_inj`

```
jupyter notebook examples/distgen_impact_cu_inj/RunModel.ipynb
```

# Impact dashboard

At present, the dashboard breaks if the results table is empty, so wait until your first run has finished! First, we'll set the `DASHBOARD_DIR` env variable to point to the directory where our impact dashboard images are saved and then we'll install the helm chart using the values in `impact-dashboard/values.yaml`. If you take a look at this file, you'll see the mongo networking variables are configured inside this file. We'll migrate towards secrets for a real deployment.
```
export DASHBOARD_DIR=$(pwd)/examples/distgen_impact_cu_inj/files/output/dashboard
helm install impact-dashboard impact-dashboard -f impact-dashboard/values.yaml --set dashboard_hostdir=$DASHBOARD_DIR
```

In another window, set up the port forwarding from the cluster to local machine:
```
kubectl port-forward $(kubectl get pods | grep impact-dashboard | awk '{n=split($2,b," "); print $1}') 8050:8050 
```

Now open:
http://localhost:8050