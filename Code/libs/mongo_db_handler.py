import pymongo
from pymongo import MongoClient, errors
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
            return self.__exception_message__ + str(e)

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
            return self.__exception_message__ + str(e)

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
            return {'response': "user already exists" + self.__messages__.nok_string_raw}

        except Exception as e:
            return {'response': "MongoDB error" + "Exception: " + str(e) + self.__messages__.nok_string_raw}

        return {'response': self.__messages__.build_ok_user_string(user_name=user_name) if status.acknowledged else \
            self.__messages__.nok_string}

    def get_collections(self):

        users = {}
        # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient

        db = self.__mongo_client__.GED

        try:
            collection_names = db.list_collection_names()
            return {"collection_names": collection_names}

        except Exception as e:
            return self.__exception_message__ + str(e)

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

    def from_df_to_mongo_meps(self, collection_name: str, df: pd.DataFrame):
        db = self.__mongo_client__.MEPS

        collection_handler = getattr(db, collection_name)

        try:
            collection_handler.create_index(
                [
                    ('MEP Name', pymongo.ASCENDING),
                    ('MEP nationalPoliticalGroup', pymongo.ASCENDING),
                    ('MEP politicalGroup', pymongo.ASCENDING),
                    ('Title', pymongo.ASCENDING),
                    ('Date', pymongo.ASCENDING),
                    ('Place', pymongo.ASCENDING),
                    ('Capacity', pymongo.ASCENDING),
                    ('Meeting With', pymongo.ASCENDING),
                    ('Meeting Related to Procedure', pymongo.ASCENDING)
                ], unique = True)

            collection_handler.insert_many(df.to_dict('records'), ordered=False)

        except Exception as e:
            print("Exception in pushing meps documents in Mongo" + str(e))
            return {"ged_insert_status": "Exception in pushing meps documents in Mongo" + str(e)}

    def from_mongo_to_xlsx(self, db_name: str, collection_name: str, query: dict):

        client = self.__mongo_client__
        db = client[db_name]
        collection = db[collection_name]

        try:
            data = list(collection.find(query, {'_id': False}))
            df = pd.DataFrame(data)
            if 'Date' in df.columns:
                df['Date'] = df['Date'].dt.strftime('%d/%m/%Y')
            else:
                print('No Date column')

            # Création d'un fichier Excel
            excel_file_path = 'export_file.xlsx'  # Spécifiez le chemin et le nom de fichier souhaités
            df.to_excel(excel_file_path, index=False)
            return True

        except Exception as e:
            print("Exception in getting meps documents in Mongo" + str(e))
            return {"ged_insert_status": "Exception in getting meps documents in Mongo" + str(e)}

    def get_unique_values(self, db_name: str, collection_name: str, fields: list):

        # Connexion à la base de données MongoDB
        client = self.__mongo_client__
        db = client[db_name]
        collection = db[collection_name]

        # Initialiser un dictionnaire pour stocker les valeurs uniques
        # Dictionnaire pour stocker les valeurs dédupliquées pour chaque champ
        valeurs_dedupliquees = {}

        # Récupérer les valeurs dédupliquées pour chaque champ
        for field in fields:
            valeurs = collection.distinct(field)
            valeurs_conformes = []
            for val in valeurs:
                if not isinstance(val, str):
                    val = str(val)
                # Tronquer la chaîne si elle dépasse 50 caractères et ajouter "..."
                valeurs_conformes.append(val)

            valeurs_dedupliquees[field] = valeurs_conformes


        return valeurs_dedupliquees

    def get_df(self, db_name: str, collection_name: str, query: dict):

        client = self.__mongo_client__
        db = client[db_name]
        collection = db[collection_name]

        try:
            data = list(collection.find(query, {'_id': False}))
            df = pd.DataFrame(data)
            if 'Date' in df.columns:
                df['Date'] = df['Date'].dt.strftime('%d/%m/%Y')
            else:
                print('No Date column')

            return df

        except Exception as e:
            print("Exception in getting meps documents in Mongo" + str(e))
            return {"ged_insert_status": "Exception in getting meps documents in Mongo" + str(e)}

    def get_df_grouped_by_month(self,
                                db_name: str,
                                collection_name: str,
                                query: dict,
                                date_start: datetime.datetime,
                                date_end: datetime.datetime):

        def get_first_day_of_next_month(date):
            """ Retourne le premier jour du mois suivant pour une date donnée. """
            if date.month == 12:
                return datetime.datetime(date.year + 1, 1, 1)
            else:
                return datetime.datetime(date.year, date.month + 1, 1)

        def get_last_day_of_month(date):
            """ Retourne le dernier jour d'un mois pour une date donnée. """
            next_month_start = get_first_day_of_next_month(date)
            return next_month_start - datetime.timedelta(days=1)

        if date_start is None:
            date_start = datetime.datetime(2010, 1, 1)
        if date_end is None:
            date_end = datetime.datetime.now()


        client = self.__mongo_client__
        db = client[db_name]
        collection = db[collection_name]
        cumulated_data = {};
        try:

            current_date = get_first_day_of_next_month(date_start)
            dates = []

            while current_date < date_end.replace(tzinfo=None):
                start_of_month = current_date
                end_of_month = get_last_day_of_month(current_date)
                dates.append((start_of_month, end_of_month))
                current_date = get_first_day_of_next_month(current_date)

            for date in dates:
                query['Date'] = {'$gte': date[0], '$lte': date[1]}
                data = list(collection.find(query, {'_id': False}))
                df = pd.DataFrame(data)

                if 'Date' in df.columns:
                    df['Date'] = df['Date'].dt.strftime('%d/%m/%Y')

                if data:
                    cumulated_data[date[0].strftime('%Y-%m-%d')] = df

            return cumulated_data

        except Exception as e:
            print("Exception in getting meps documents in Mongo" + str(e))
            return {"ged_insert_status": "Exception in getting meps documents in Mongo" + str(e)}
