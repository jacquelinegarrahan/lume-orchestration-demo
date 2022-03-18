# Demo: lcls_cu_inj_nn

A model of the copper injector has been packaged for compatability with the LUME/SLAC services [here](https://github.com/jacquelinegarrahan/lcls-cu-inj-nn-ex).

```
$ save-model examples/lcls_cu_inj_nn/lcls_cu_inj_nn.yaml
```

The command with output a model id associated with the saved model. Export this value to the environment variable `LCLS_CU_INJ_NN_MODEL_ID`:

```
export LCLS_CU_INJ_NN_MODEL_ID={save-model output model ID}
```

You can check the model entry in the database directly by logging into mysql to check the model has been saved:
```
mysql -u root -h 127.0.0.1 -ppassword
use model_db
select * from models;
```

Now, lets create an entry for the versioned deployment using the model_id. Deployments are associated with tagged releases of a stored model. 

Inside examples/lcls_cu_inj_nn/deployment.yaml you'll find:
```yaml

model_version: 
  version: v0.X
  url: https://github.com/jacquelinegarrahan/lcls-cu-inj-nn-ex
  model_id: X
  package_name: lcls_cu_inj_nn_ex
```
The version entry corresponds with the release version, the url responds to the github repo, model ID to the previously created model id entry, and package name to the importable package name. This will probably be cleaned up in later iterations with better package management, but now functions by looking for two entrypoints packaged with the distribution: `get_flow` and `model`, which serve to return the packaged flow and model object, respectively. You may find these in the repository `setup.py` [here](https://github.com/jacquelinegarrahan/lcls-cu-inj-nn-ex/blob/e074494847f2e31a30f8b1a64d80e96884ece941/setup.py#L25).

```
save-model-deployment examples/lcls_cu_inj_nn/deployment.yaml
```

Save this deployment id to an environment variable:
```
export LCLS_CU_INJ_NN_DEPLOYMENT_ID={save-model-deployment output deployment ID}
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
save-deployment-flow $LCLS_CU_INJ_NN_DEPLOYMENT_ID my-models
```

## Open notebook


```
jupyter notebook
```