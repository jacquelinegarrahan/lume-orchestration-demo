from slac_services.scheduling import schedule_flow_run
# assumes you have registered a flow named "example" in a project named "my-example-project"

flow_run = schedule_flow_run("my-example-flow", "my-example-project", None)
