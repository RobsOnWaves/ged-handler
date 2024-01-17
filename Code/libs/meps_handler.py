import datetime
import re
import threading
from io import BytesIO

import numpy as np
import pandas as pd
from docx import Document
from fastapi import UploadFile
from libs.messages import Messages
from openpyxl import load_workbook
from openpyxl.styles import Alignment
from unidecode import unidecode
import shutil
import tempfile


class MepsHandler:
    def __init__(self):
        self.__messages__ = Messages()
        self.__max_length__ = 1000
        self.__timeout_duration__ = 60
        self.__mep_field_list__ = ["MEP Name", "MEP nationalPoliticalGroup", "MEP politicalGroup", "Title", "Place",
                                   "Meeting With", "Meeting Related to Procedure"]
        self.__mep_db_name__ = "MEPS"
        self.__collection_name__ = "meps_meetings"

    class TimeoutException(Exception):
            pass

    def timeout_handler(self):
        raise self.TimeoutException()

    async def load_csv_file(self, upload_file: UploadFile, answer: dict = None):

        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            # Copier le contenu de l'objet UploadFile dans le fichier temporaire
            shutil.copyfileobj(upload_file.file, temp_file)
            temp_file_path = temp_file.name

        # Extract the table
        timer = threading.Timer(self.__timeout_duration__, self.timeout_handler)
        try:
            timer.start()
            df = pd.read_csv(temp_file_path)
            df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')
            df['Date'] = df['Date'].fillna(pd.to_datetime("01-01-1970"))
            answer["df"] = df
            answer["success"] = True
            return answer
        except self.TimeoutException:
            answer["df"] = None
            answer["success"] = False
            return self.__messages__.nok_string
        finally:
            # Arrête le timer
            timer.cancel()

