from libs.mongo_db_handler import MongoDbGed
from libs.ged_file_handler import GedFileHandler
from pathlib import Path
if __name__ == '__main__':
    print('Welcome to the GED handler')

    mongo_handler = MongoDbGed(address='localhost:27017', user='root', password='rootpwdmongo')

    mongo_handler.whoami()

    ged_handler = GedFileHandler(Path('./data_in/ged_in.ged'))

    print(str(ged_handler.get_filename()))

    ged_handler.to_dict()
