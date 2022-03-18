# TODO

## HIGH
- Update all examples to use paths relative to the package directory for repeatability
- Update older examples to use newer services (keep simple dockerfile one)
- Port forwarding on dashboard occasionally crashes ?
- Dashboard itself sometimes silently crashes
- Notebook for distgen predict
- Fill out demo instructions
- Add results storage to the neural network model

## LOWER
- Dockerfile to install versions
- Research caching
- Adapt Bmad
- Use LocalResults for file saving in distgen example
- Fix object passing to distgen directly
- Enforce unique keys in model db
- Convert model fingerprint to unique in results_db
- Look up mongo performance optimization... binary data?
- Create ticket for Prefect UI integer labels
- consistent 'file' naming scheme for disgen inputs-> impact_archive_file vs. disgen_input_filename
- Do not conda install each time, check for existing installation. Will have to figure out import name dash vs underscore
- Should not have to install package for remote model if flow is already registered
- Add lowercase RFC 1123 enforcement to mount names (no _ allowed)
- Toy example for Colwyn broken assignment
- As of now, dashboard must be started with some data already in the db, which is annoying. Fix.
- Move model url to model table and then use tag to find path

## Other for modeling service
- Directory service file generator
- Served pvs for output
- Execution process for queuing new simulations (configurable with local/remote modeling service)
- Logging service for somehow getting these into the EPICS logging service 
- Separate lume-services from slac-services
- Authentication btw pods should be intelligently handled. I'm passing mongo auth to dashboard right now as username/ password ?

# DONE:
- Service configuration file must be mounted 
- Add env var for configuration file 
- Create helm chart for dashboard 
- Mongo interface 
- Lume-model needs to be updated to properly parse arrays 
- switch to conda environment +
- Fill in pv values for distgen demo
- Copy isotime utility from impact -> utils in slac_services, unnecessary dependency
- Fix CPU constraint on job. Impact jobs taking far too long
- Created deployment for impact dashboard
- Abstract kind configuration paths (to be configured by user)
- Update all examples to use consistent formatting (ex. lcls-cu-inj vs lcls_cu_inj)
- Add versioning to impact dashboard docker
- Check deployment of impact dashboard
- Fix dropdown text coloring for dockerized dashboard
- Update config with relative path
- Use complete DB_URI for model_db
- Fix dashboard naming scheme for impact- reduncdant isotime
- change function name to archive_impact
- Distgen-impact versioned docker build
- NN versioned docker build
- Adapt the lcls-cu-inj-ex to use conda environment installation
- fix versioning for docker flow builds- have to be installed from tagged release... need to install version in docker & drop from evironment. docker build yml ARG
- Fill in pv values for nn demo
- versioneer for slac_services 
- Fix conda installation bug 
- Fix distgen versioneer
