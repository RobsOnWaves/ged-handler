from libs.mongo_db_handler import MongoDbGed
from libs.ged_file_handler import GedFileHandler
from pathlib import Path

if __name__ == '__main__':
    print('Welcome to the GED handler')

    mongo_handler = MongoDbGed(address='localhost:27017', user='root', password='rootmongopwd')

    ged_handler = GedFileHandler(Path('./data_in/ged_in.ged'))

    mongo_handler.insert_list_of_ged_objets(ged_handler, collection_name='benichman')

    person = GedFileHandler.Person

    person.family_name = 'family_name1'
    person.given_names = ['given_1', 'given_2']

    ged_handler.add_person(person)
