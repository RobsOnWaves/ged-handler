from pymongo import MongoClient
from libs.ged_file_handler import GedFileHandler
import datetime

class MongoDbGed:

    def __init__(self, address: str, user: str, password: str):
        self.__address__ = address
        self.__user__ = user
        self.__password__ = password
        self.__connection_string__ = "mongodb://" + user + ":" + password + "@" + address
        self.__mongo_client__ = MongoClient(self.__connection_string__)

    def from_ged_dict_to_mongodb_dict(self, ged_handler: GedFileHandler):
        mongo_adapted_ged_list_object = ged_handler.listed_documents
        for index, ged_object in enumerate(mongo_adapted_ged_list_object):
            if 'marriage' in ged_object:
                mongo_adapted_ged_list_object[index]['marriage']['date_info']['date'] =\
                    datetime.datetime.combine(ged_object['marriage']['date_info']['date'], datetime.time.min)
            if 'birth' in ged_object:
                mongo_adapted_ged_list_object[index]['birth']['date_info']['date'] =\
                    datetime.datetime.combine(ged_object['birth']['date_info']['date'], datetime.time.min)
            if 'death' in ged_object:
                mongo_adapted_ged_list_object[index]['death']['date_info']['date'] =\
                    datetime.datetime.combine(ged_object['death']['date_info']['date'], datetime.time.min)

        return mongo_adapted_ged_list_object

    def insert_list_of_ged_objets(self, ged_handler: GedFileHandler, collection_name: str):
        db = self.__mongo_client__.GED
        collection_handler = getattr(db, collection_name)
        ged_objects = self.from_ged_dict_to_mongodb_dict(ged_handler)
        cursor = collection_handler.insert_many(ged_objects)

        if cursor.acknowledged is True:
            return {"ged_insert_status": "Insertions with success"}

        elif cursor.acknowledged is not True:
            return {"ged_insert_status": "Insertions_not_ended_mongoDB did not acknowledged"}

        elif cursor.matched_count == 0:
            return {"ged_insert_status": "Insertionsn_not_ended_mongoDB no document matched"}
