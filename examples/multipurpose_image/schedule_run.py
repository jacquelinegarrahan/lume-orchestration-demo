from slac_services.scheduling import schedule_flow_run
# assumes you have registered a flow named "example" in a project named "my-example-project"

flow_run1 = schedule_flow_run("my-example-flow1", "my-example-mp-project", None)

flow_run2 = schedule_flow_run("my-example-flow2", "my-example-mp-project", None)

flow_run3 = schedule_flow_run("my-example-flow3", "my-example-mp-project", None)