from slac_services import service_container
from slac_services.services.scheduling import MountPoint


mount_point = MountPoint(name="fs-test", host_path="/Users/jgarra/sandbox", mount_type="Directory")
    
scheduler = service_container.prefect_scheduler()
lume_configuration_file = "/Users/jgarra/sandbox/lume-orchestration-demo/examples/config.yaml"

scheduler.schedule_run(flow_id="04728cdd-c6d3-4f65-8cd7-89b902ee6ac7", data= {}, mount_points=[mount_point], lume_configuration_file=lume_configuration_file)