from libs.mongo_db_handler import MongoDbGed
from libs.ged_file_handler import GedFileHandler
from pathlib import Path

if __name__ == '__main__':
    print('Welcome to the GED handler')

    mongo_handler = MongoDbGed(address='localhost:27017', user='root', password='rootmongopwd')

    ged_handler = GedFileHandler()

    ged_handler.from_file_to_list_of_dict(Path('./data_in/ged_in.ged'))

    mongo_handler.insert_list_of_ged_objets(ged_handler, collection_name='coll_name')

    person = GedFileHandler.Person

    person.family_name = 'family_name1'
    person.given_names = ['given_1', 'given_2']

    ged_handler.add_person(person)

    ged_listed_dict = mongo_handler.from_mongo_to_ged_list_dict('coll_name')

    ged_handler_to_modify = GedFileHandler()

    ged_handler_to_modify.load_ged_listed_dict(ged_listed_dict)




