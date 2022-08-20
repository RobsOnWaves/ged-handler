from pymongo import MongoClient


class MongoDbGed:

    def __init__(self, address: str, user: str, password: str):
        self.__address__ = address
        self.__user__ = user
        self.__password__ = password
        self.__connection_string__ = "mongodb://" + user + ":" + password + "@" + address
        self.__mongo_client__ = MongoClient(self.__connection_string__)

    def add_list_of_ged_objets(self, ged_objects: [dict], collection_name: str):
        db = self.__mongo_client__.GED
        collection_handler = getattr(db, collection_name)
        cursor = collection_handler.insert_many(ged_objects)

        if cursor.acknowledged is True:
            return {"ged_insert_status": "Insertions with success"}

        elif cursor.acknowledged is not True:
            return {"ged_insert_status": "Insertions_not_ended_mongoDB did not acknowledged"}

        elif cursor.matched_count == 0:
            return {"ged_insert_status": "Insertionsn_not_ended_mongoDB no document matched"}
