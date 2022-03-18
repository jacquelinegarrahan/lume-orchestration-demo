from slac_services.config import initialize_services

service_container = initialize_services()

service_container.wire(packages=["slac_services.scripts.models"])


from . import _version
__version__ = _version.get_versions()['version']
