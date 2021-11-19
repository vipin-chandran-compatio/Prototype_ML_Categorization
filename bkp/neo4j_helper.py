from neo4j import GraphDatabase
import neo4j
#import settings


class neo4j_helper:
    __db_name = None

    def __init__(self, dbName):
        print(1)
        self.__db_name = dbName
        self.driver = GraphDatabase.driver("bolt://localhost:7474", auth=("vipingraph1", "vipingraph1"))

    # def close(self):
    #     # Don't forget to close the driver connection when you are finished with it
    #     self.driver.close()

    def execute(self, query):
        if query is None:
            return

        if type(query) == str:
            with self.driver.session(database=self.__db_name, default_access_mode=neo4j.WRITE_ACCESS) as session:
                session.run(query)

        if type(query) == list:
            with self.driver.session(database=self.__db_name, default_access_mode=neo4j.WRITE_ACCESS) as session:
                tx = session.begin_transaction()
                try:
                    for q in query:
                        tx.run(q)
                    tx.commit()
                    tx.close()
                except Exception as e:
                    tx.rollback()
                    tx.close()
                    raise Exception(str(e))

    def query(self, query):
        with self.driver.session(database=self.__db_name, default_access_mode=neo4j.READ_ACCESS) as session:
            result = session.run(query)
            return [record for record in result]