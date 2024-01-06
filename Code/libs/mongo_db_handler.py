from pymongo import MongoClient
from libs.ged_file_handler import GedFileHandler
from libs.messages import Messages
import pandas as pd
import datetime
import copy


class MongoDbGed:

    def __init__(self, address: str, user: str, password: str):
        self.__address__ = address
        self.__user__ = user
        self.__password__ = password
        self.__connection_string__ = "mongodb://" + user + ":" + password + "@" + address
        self.__mongo_client__ = MongoClient(self.__connection_string__)
        self.__messages__ = Messages()
        self.__exception_message__ = "MongoDB error Exception: "

    def get_gold_coeffs(self):
        db = self.__mongo_client__.gold_coeffs

        try:
            gold_coeffs = db["gold_coeffs"].find_one()
            return gold_coeffs

        except Exception as e:
            return self.__exception_message__+ str(e)

    @staticmethod
    def from_ged_dict_to_mongodb_dict(ged_handler: GedFileHandler = GedFileHandler(),
                                      ged_list_of_dict=None):

        if ged_list_of_dict is None:
            ged_list_of_dict = []

        if ged_handler.listed_documents:
            mongo_adapted_ged_list_object = copy.deepcopy(ged_handler.listed_documents)

        elif ged_list_of_dict:
            mongo_adapted_ged_list_object = ged_list_of_dict

        for index, ged_object in enumerate(mongo_adapted_ged_list_object):
            if 'marriage' in ged_object:
                try:
                    if 'date_info' in mongo_adapted_ged_list_object[index]['marriage']:
                        mongo_adapted_ged_list_object[index]['marriage']['date_info']['date'] = \
                            datetime.datetime.combine(ged_object['marriage']['date_info']['date'], datetime.time.min)
                except Exception as e:
                    print('Exception in transforming ged dict to mongo object marriage:' + str(e))

            if 'birth' in ged_object:
                try:
                    if 'date_info' in mongo_adapted_ged_list_object[index]['birth']:
                        mongo_adapted_ged_list_object[index]['birth']['date_info']['date'] = \
                            datetime.datetime.combine(ged_object['birth']['date_info']['date'], datetime.time.min)
                except Exception as e:
                    print('Exception in transforming ged dict to mongo object birth:' + str(e))

            if 'death' in ged_object:
                try:
                    if 'date_info' in mongo_adapted_ged_list_object[index]['death']:
                        mongo_adapted_ged_list_object[index]['death']['date_info']['date'] = \
                            datetime.datetime.combine(ged_object['death']['date_info']['date'], datetime.time.min)
                except Exception as e:
                    print('Exception in transforming ged dict to mongo object death:' + str(e))

        return mongo_adapted_ged_list_object

    @staticmethod
    def from_mongodb_dict_to_ged_dict(raw_mongo_list: [dict]):

        for index, ged_object in enumerate(raw_mongo_list):
            if 'marriage' in ged_object:
                try:
                    if 'date_info' in raw_mongo_list[index]['marriage']:
                        raw_mongo_list[index]['marriage']['date_info']['date'] = \
                            ged_object['marriage']['date_info']['date'].date()

                except Exception as e:
                    print('Exception in transforming mongo object to ged dict marriage:' + str(e))

            if 'birth' in ged_object:
                try:
                    if 'date_info' in raw_mongo_list[index]['birth']:
                        raw_mongo_list[index]['birth']['date_info']['date'] = \
                            ged_object['birth']['date_info']['date'].date()

                except Exception as e:
                    print('Exception in transforming mongo object to ged dict birth:' + str(e))

            if 'death' in ged_object:
                try:
                    if 'date_info' in raw_mongo_list[index]['death']:
                        raw_mongo_list[index]['death']['date_info']['date'] = \
                            ged_object['death']['date_info']['date'].date()

                except Exception as e:
                    print('Exception in transforming mongo object to ged dict death:' + str(e))

        return raw_mongo_list

    def insert_list_of_ged_objets(self,
                                  collection_name: str,
                                  ged_list_of_dict=None,
                                  ged_handler: GedFileHandler = GedFileHandler()):
        if ged_list_of_dict is None:
            ged_list_of_dict = []
        db = self.__mongo_client__.GED
        collection_handler = getattr(db, collection_name)

        if ged_handler.listed_documents:
            ged_list_of_dict = self.from_ged_dict_to_mongodb_dict(ged_handler)
        try:
            collection_handler.create_index('ged_id', unique=True)
        except Exception as e:
            print("Exception in creating Mongo index" + str(e))

        try:
            cursor = collection_handler.insert_many(ged_list_of_dict)

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

    def get_users(self):

        users = {}
        # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient

        db = self.__mongo_client__.USERS

        try:
            cursor = db.users.find()
            end_cursor = False
            while not end_cursor:
                try:
                    users.update(cursor.next())
                except StopIteration:
                    print('end loop')
                    end_cursor = True
                except Exception as e:
                    print(e)
                    end_cursor = True

        except Exception as e:
            return self.__exception_message__+ str(e)

        return users

    def insert_user(self,
                    user_name,
                    full_name,
                    email,
                    hashed_password,
                    creator,
                    role
                    ):

        db = self.__mongo_client__.USERS

        query = {
            "user_name": user_name,
            user_name:
                {
                    "username": user_name,
                    "full_name": full_name,
                    "email": email,
                    "hashed_password": hashed_password,
                    "disabled": False,
                    "created_at": datetime.datetime.utcnow(),
                    "created_by": creator,
                    "role": role
                }
        }

        try:
            status = db.users.insert_one(query)

        except errors.DuplicateKeyError as e:
            return {'response': "user already exists" + self.__messages__.nok_string}

        except Exception as e:
            return {'response': "MongoDB error" + "Exception: " + str(e) + self.__messages__.nok_string}

        return self.__messages__.build_ok_user_string(user_name=user_name) if status.acknowledged else \
            self.__messages__.nok_string

    def get_collections(self):

        users = {}
        # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient

        db = self.__mongo_client__.GED

        try:
            collection_names = db.list_collection_names()
            return {"collection_names": collection_names}

        except Exception as e:
            return self.__exception_message__+ str(e)

    def modify_user_password(self,
                             user_name: str,
                             hashed_password: str
                             ):

        db = self.__mongo_client__.USERS

        try:
            status = db.users.update_one({
                "user_name": user_name},
                {"$set": {user_name + ".hashed_password": hashed_password}})

        except errors.DuplicateKeyError as e:
            return {'response': "user already exists" + self.__messages__.nok_string}

        except Exception as e:
            return {'response': "MongoDB error" + "Exception: " + str(e) + self.__messages__.nok_string}

        return self.__messages__.build_ok_user_modified_string(user_name=user_name) if status.acknowledged else \
            self.__messages__.nok_string

    def from_df_to_mongo(self, collection_name: str, df: pd.DataFrame):
        db = self.__mongo_client__.MEPS

        collection_handler = getattr(db, collection_name)

        try:
            collection_handler.insert_many(df.to_dict('records'))

        except Exception as e:
            print("Exception in pushing meps documents in Mongo" + str(e))
            return {"ged_insert_status": "Exception in pushing meps documents in Mongo" + str(e)}
