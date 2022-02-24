


class MongoDBConfig():

    def __init__():
        ...


class MongoDB():

    def __init__(self, config: MongoDBConfig):
        self.config = config

        self._establish_connection()


    def _establish_connection(self):
        ...