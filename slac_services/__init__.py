from slac_services.config import initialize_services

service_container = initialize_services()

service_container.wire(packages=["slac_services.scripts.models"])

