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
import nltk
from nltk.corpus import stopwords
from collections import Counter



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

    def get_mep_field_list(self):
        return self.__mep_field_list__

    def get_mep_db_name(self):
        return self.__mep_db_name__

    def get_mep_collection_name(self):
        return self.__collection_name__

    def get_stats(self, df: pd.DataFrame):
        stats = {}
        nltk.download('stopwords')
        stop_words = set(stopwords.words('english'))
        stop_words.update(set(stopwords.words('french')))
        stop_words.update(set(stopwords.words('spanish')))
        stop_words.update(set(stopwords.words('italian')))
        stop_words.update(set(stopwords.words('portuguese')))
        stop_words.update(set(stopwords.words('german')))
        stop_words.update(set(stopwords.words('dutch')))
        stop_words.update(set(stopwords.words('russian')))
        stop_words.update(set(stopwords.words('finnish')))
        df = df.replace(to_replace='[-/&()]', value=' ', regex=True)
        df["Meeting Related to Procedure"] = df["Meeting Related to Procedure"].replace(to_replace=pd.NA,
                                                                                        value='Not related to a procedure'
                                                                                    )
        def convert_numbers_to_string(x):
            if isinstance(x, float):
                return str(x)
            if isinstance(x, int):
                return str(x)
            return x
        def count_words(text_series):
            all_words = []
            for line in text_series:
                words = line.lower().split()
                words = [word.strip('.,;!') for word in words if word.lower() not in stop_words]
                all_words.extend(words)
            return Counter(all_words)

        df = df.map(convert_numbers_to_string)

        for column in ["Title", "Meeting With"]:
            occurrences_counter = count_words(df[column])
            stats[column] = Counter(
                {k: v for k, v in sorted(occurrences_counter.items(), key=lambda item: item[1], reverse=True)})
        for column in ["MEP Name",
                       "MEP nationalPoliticalGroup",
                       "MEP politicalGroup",
                       "Place",
                       "Meeting Related to Procedure"]:
            occurrences_counter = Counter(df[column])
            stats[column] = Counter(
                {k: v for k, v in sorted(occurrences_counter.items(), key=lambda item: item[1], reverse=True)})

        return stats
