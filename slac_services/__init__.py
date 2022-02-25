from slac_services.config import initialize_services, SLACServices

services = initialize_services()

services.wire(packages=["slac_services.scripts.models"])