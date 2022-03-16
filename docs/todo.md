# TODO

## HIGH
- Check deployment of impact dashboard
- Update all examples to use consistent formatting (ex. lcls-cu-inj vs lcls_cu_inj)
- Update all examples to use paths relative to the package directory for repeatability
- Adapt the lcls-cu-inj-ex to use conda environments
- Add versioning to the docker builds
    - Impact dashboard
    - Flows
- Copy isotime utility from impact -> utils in slac_services, unnecessary dependency
- Fill in correct PV names for demo, currently using dummys
- Update older examples to use newer services

## LOWER
- Research caching
- Adapt Bmad
- Use LocalResults for file saving in distgen example
- Fix object passing to distgen directly
- Enforce unique keys in model db
- Convert model fingerprint to unique in results_db
- Look up `what is appropriate to store in Mongodb`
- Create ticket for Prefect UI integer labels
- consistent 'file' naming scheme for disgen inputs-> impact_archive_file vs. disgen_input_filename

# DONE:
- Service configuration file must be mounted 
- Add env var for configuration file 
- Create helm chart for dashboard 
- Mongo interface 
- Lume-model needs to be updated to properly parse arrays 
- Create dashboards 
- switch to conda environment +
- Create dashboard helm chart 