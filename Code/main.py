from libs.mongo_db_handler import MongoDbGed


if __name__ == '__main__':
    print('Welcome to the GED handler')

    mongo_handler = MongoDbGed(address='localhost:27017', user='root', password='rootpwdmongo')

    mongo_handler.whoami()

