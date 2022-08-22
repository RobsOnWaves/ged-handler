from libs.mongo_db_handler import MongoDbGed
from libs.ged_file_handler import GedFileHandler
from pathlib import Path

if __name__ == '__main__':
    print('Welcome to the GED handler')

    mongo_handler = MongoDbGed(address='localhost:27017', user='root', password='rootmongopwd')

    ged_handler = GedFileHandler()

    ged_handler.from_file_to_list_of_dict(Path('./data_in/ged_in.ged'))

    mongo_handler.insert_list_of_ged_objets(collection_name='coll_name', ged_handler=ged_handler)

    person1 = GedFileHandler.Person

    person1.family_name = 'family_name1'
    person1.given_names = ['given_1', 'given_2']

    person2 = GedFileHandler.Person

    person2.family_name = 'family_name2'
    person2.given_names = ['given_1', 'given_2']

    family1 = GedFileHandler.Family

    family1.husband = ['123456']
    family1.wife = ['1213313']
    family1.children = ['12311414', '1232444']

    family2 = GedFileHandler.Family

    family2.husband = ['012345644']
    family2.wife = ['0121331344']
    family2.children = ['01231141444', '0123244433']

    ged_listed_dict = mongo_handler.from_mongo_to_ged_list_dict('coll_name')

    ged_handler_to_modify = GedFileHandler()

    ged_handler_to_modify.load_ged_listed_dict(ged_listed_dict)

    persons_documents = ged_handler_to_modify.add_persons([person1, person2])

    families_documents = ged_handler_to_modify.add_families([family2, family1])

    mongo_handler.insert_list_of_ged_objets(collection_name='coll_name', ged_list_of_dict=[persons_documents[0]])

    mongo_handler.insert_list_of_ged_objets(collection_name='coll_name', ged_list_of_dict=[persons_documents[1]])

    mongo_handler.insert_list_of_ged_objets(collection_name='coll_name', ged_list_of_dict=[families_documents[0]])

    mongo_handler.insert_list_of_ged_objets(collection_name='coll_name', ged_list_of_dict=[families_documents[1]])
