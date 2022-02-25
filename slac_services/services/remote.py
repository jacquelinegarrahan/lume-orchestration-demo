from contextlib import contextmanager
from pydantic import BaseSettings
from sshtunnel import open_tunnel
import os


class RemoteEPICSConnectionConfig(BaseSettings):
    host: str
    host_port: int
    local_port: int
    hop_host: str
    user: str
    password_file: str

class RemoteEPICSConnectionService:
    def __init__(self, *, host, host_port, local_port, hop_host, user, password_file):
        self._user = user
        self._password_file = password_file
        self._host = host
        self._host_port = host_port
        self._local_port = local_port
        self._hop_host = hop_host

    @contextmanager
    def connection(self):

        os.environ["CA_NAME_SERVER_PORT"] = self._local_port
        
        with open(self._password_file, "r") as f:
            password = f.read()

        try:

            with open_tunnel(
                (self._hop_host, 22),
                remote_bind_address=(self._host, self._host_port),
                local_bind_address=("localhost", self._local_port),
                ssh_username=self._user,
                ssh_password=password,
                ) as conn:

                    yield conn

        finally:
            print(f"Tunnel to {self._host} closed.")

    
    def get_epics_snapshot(self, epics_configuration):

        with self.connection() as conn:
            ...