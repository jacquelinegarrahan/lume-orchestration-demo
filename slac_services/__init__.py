from slac_services.config import initialize_services
from pkg_resources import resource_filename

service_container = initialize_services()

service_container.wire(packages=["slac_services.scripts.models"])


SDF_RUN_SPEC  = resource_filename(
    "slac_services.files", "kubernetes_job.yaml"
)