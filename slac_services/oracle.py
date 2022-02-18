import cx_Oracle
import os


class OracleDBConfig():
    def __init__(self, two_task: str, oracle_home: str, tns_admin: str, ld_library_path: str = None):
        self.two_task = two_task
        self.oracle_home = oracle_home
        self.tns_admin = tns_admin
        self.ld_library_path = ld_library_path


class OracleReadableDB():
    def __init__(self, config: OracleDBConfig):
        self.config = config

        if not self.config.two_task:
            raise ValueError("Missing two task definition")

        if not self.config.oracle_home:
            raise ValueError("Missing oracle home definition")

        if not self.config.tns_admin:
            raise ValueError("Missing tns admin definition")

        if not self.config.ld_library_path:
            raise ValueError("Missing ld library path definition")

        
        os.environ["TWO_TASK"] = self.config.two_task
        os.environ["ORACLE_HOME"] = self.config.oracle_home
        os.environ["TNS_ADMIN"] = self.config.tns_admin

        # update paths
        ld_path = os.environ.get("LD_LIBRARY_PATH")

        if ld_path:
            os.environ["LD_LIBRARY_PATH"] = self.config.oracle_home + "/lib:" + ld_path
        else:
            os.environ["LD_LIBRARY_PATH"] =  self.config.oracle_home + "/lib"

        os.environ["PATH"] =  self.config.oracle_home + "/bin:"+os.environ["PATH"]

        self._establish_connection()

    
    def _establish_connection(self):
        self._conn = cx_Oracle.connect("/@SLACPROD")
        self._db = self._conn.cursor()


class OracleWritableDB(OracleReadableDB):
    ...
    def execute(sqlstatement):
        ...
        self._db.execute(sqlstatement)
        data = self._db.fetchall()

