from pymongo import MongoClient
from libs.ged_file_handler import GedFileHandler
import datetime
import copy


class MongoDbGed:

    def __init__(self, address: str, user: str, password: str):
        self.__address__ = address
        self.__user__ = user
        self.__password__ = password
        self.__connection_string__ = "mongodb://" + user + ":" + password + "@" + address
        self.__mongo_client__ = MongoClient(self.__connection_string__)

    @staticmethod
    def from_ged_dict_to_mongodb_dict(ged_handler: GedFileHandler):
        mongo_adapted_ged_list_object = copy.deepcopy(ged_handler.listed_documents)

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

    @staticmethod
    def from_mongodb_dict_to_ged_dict(raw_mongo_list: [dict]):

        for index, ged_object in enumerate(raw_mongo_list):
            if 'marriage' in ged_object:
                raw_mongo_list[index]['marriage']['date_info']['date'] =\
                    ged_object['marriage']['date_info']['date'].date()
            if 'birth' in ged_object:
                raw_mongo_list[index]['birth']['date_info']['date'] =\
                    ged_object['birth']['date_info']['date'].date()
            if 'death' in ged_object:
                raw_mongo_list[index]['death']['date_info']['date'] =\
                    ged_object['death']['date_info']['date'].date()

        return raw_mongo_list

    def insert_list_of_ged_objets(self, ged_handler: GedFileHandler, collection_name: str):
        db = self.__mongo_client__.GED
        collection_handler = getattr(db, collection_name)
        ged_objects = self.from_ged_dict_to_mongodb_dict(ged_handler)
        try:
            collection_handler.create_index('ged_id', unique=True)
        except Exception as e:
            print("Exception in creating Mongo index" + str(e))

        try:
            cursor = collection_handler.insert_many(ged_objects)

            if cursor.acknowledged is True:
                return {"ged_insert_status": "Insertions with success"}

            elif cursor.acknowledged is not True:
                return {"ged_insert_status": "Insertions_not_ended_mongoDB did not acknowledged"}

            elif cursor.matched_count == 0:
                return {"ged_insert_status": "Insertions_not_ended_mongoDB no document matched"}

        except Exception as e:
            print("Exception in pushing ged documents in Mongo" + str(e))
            return {"ged_insert_status": "Exception in pushing ged documents in Mongo" + str(e)}

    def from_mongo_to_ged_list_dict(self, collection_name: str):
        ged_list_dict = []
        db = self.__mongo_client__.GED
        collection_handler = getattr(db, collection_name)
        cursor = collection_handler.find({}, {'_id': False})

        end_cursor = False

        while not end_cursor:
            try:
                ged_list_dict.append(cursor.next())
            except StopIteration:
                print('end loop')
                end_cursor = True
            except Exception as e:
                print(e)
                end_cursor = True

        self.from_mongodb_dict_to_ged_dict(ged_list_dict)

        return ged_list_dict

