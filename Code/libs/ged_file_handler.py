from pathlib import Path
from datetime import date
import random
from fastapi import UploadFile


class GedFileHandler:

    __month_lut__ = {
        'JAN': '01',
        'FEB': '02',
        'MAR': '03',
        'APR': '04',
        'MAY': '05',
        'JUN': '06',
        'JUL': '07',
        'AUG': '08',
        'SEP': '09',
        'OCT': '10',
        'NOV': '11',
        'DEC': '12',

    }

    __links_keywords__ = ['HUSB', 'WIFE', 'CHIL', 'FAMC', 'FAMS']

    __links_lut__ = {
        'HUSB': 'husband',
        'WIFE': 'wife',
        'CHIL': 'children',
        'FAMS': 'fams',
        'FAMC': 'famc'
    }

    __sections_lut__ = {
        'HEAD': 'head',
        'SOUR': 'source',
        'VERS': 'version',
        'NAME': 'name',
        'CORP': 'corporation',
        'SUBM': 'submission_id',
        'GEDC': 'gedc',
        'FORM': 'form',
        'CHAR': 'char',
        'MARR': 'marriage',
        'BIRT': 'birth',
        'DEAT': 'death',
        'NOTE': 'note'
    }

    class Person:
        ged_id: str
        given_names: [str] = ['not defined']
        family_name: str = 'not defined'
        sex: str = 'not defined'
        birth_place: str = ['not defined']
        birth_date: date = None
        death_place: str = 'not defined'
        death_date: date = None
        date_type_birth: str = 'not defined'
        date_type_death: str = 'not defined'
        note: str = 'not defined'
        fams: [str] = ['not defined']
        famc: [str] = ['not defined']

    class Family:
        ged_id: str
        husband: [str] = ['not defined']
        wife: [str] = ['not defined']
        children: [str] = ['not defined']
        marriage_date: date = None
        date_type_marriage: str = 'not defined'

    def __init__(self):
        self.file = Path
        self.__current_document__ = {}
        self.__subsection__ = str
        self.__previous_document__ = {}
        self.listed_documents = []

    def get_filename(self):
        return self.file.name

    def __handle_new_document__(self, decomposed_line: [str]):
        # Starting a new section ?
        if decomposed_line[0] == '0':
            if decomposed_line[1] == 'HEAD':
                self.__current_document__ = {'node_type': 'head'}
            elif decomposed_line[1] == 'TRLR':
                self.listed_documents.append(self.__previous_document__)
                return 'end of file'
            else:
                try:
                    if decomposed_line[2] == 'INDI':
                        self.__current_document__ = {'node_type': 'person',
                                                     'ged_id': decomposed_line[1],
                                                     }
                    elif decomposed_line[2] == 'FAM':
                        self.__current_document__ = {'node_type': 'family', 'ged_id': decomposed_line[1]}
                    elif decomposed_line[2] == 'SUBM':
                        self.__current_document__ = {'node_type': 'subm', 'ged_id': decomposed_line[1]}

                except Exception as e:
                    print('error in parsing levels 0:' + str(e))

            if self.__current_document__['node_type'] != 'head':
                self.listed_documents.append(self.__previous_document__)
            return 'new section'

        return 'in section'

    def __handle_links__(self, link_type: str, payload: str):
        self.__handle_active_subsection__(link_type)
        if link_type in self.__current_document__:
            self.__current_document__[link_type].append(payload)
        else:
            self.__current_document__[link_type] = [payload]

    def __handle_active_subsection__(self, subsection: str):
        self.__subsection__ = subsection

    def __handle_date_place__(self, event_type: str, line_decomposed: [str], line_raw: str):
        # Initiating the event
        if event_type not in self.__current_document__:
            self.__current_document__[event_type] = {}

        if line_decomposed[1] == 'DATE':
            self.__current_document__[event_type]['date_info'] = {}

            if len(line_decomposed) == 5:  # full date

                self.__current_document__[event_type]['date_info']['date'] = date.fromisoformat(line_decomposed[4]
                                                                                                + '-' +
                                                                                                self.__month_lut__.get(
                                                                                                    line_decomposed[3])
                                                                                                + '-' +
                                                                                                (line_decomposed[2] if
                                                                                                len(line_decomposed[2])
                                                                                                == 2
                                                                                                else '0'
                                                                                                     + line_decomposed[
                                                                                                         2]))

                self.__current_document__[event_type]['date_info']['date_type'] = 'full_date'

            elif len(line_decomposed) == 3:  # only the year
                self.__current_document__[event_type]['date_info']['date'] = date.fromisoformat(line_decomposed[2]
                                                                                                + '-01-01')
                self.__current_document__[event_type]['date_info']['date_type'] = 'year_only'

            elif len(line_decomposed) == 4:  # month + year
                self.__current_document__[event_type]['date_info']['date'] = date.fromisoformat(line_decomposed[3]
                                                                                                + '-' +
                                                                                                self.__month_lut__[
                                                                                                    line_decomposed[2]]
                                                                                                + '-01')
                self.__current_document__[event_type]['date_info']['date_type'] = 'year_month_only'

            else:
                raise Exception('unhandled date line' + line_decomposed)

        if line_decomposed[1] == 'PLAC':
            try:
                self.__current_document__[event_type]['place'] = line_raw.replace('2 PLAC ', '')

            except Exception as e:
                print('Exception adding a place to the current entry:' + str(e) + 'line:' + line_raw)

    def __get_unique_ged_id__(self, node_type: str):
        existing_keys = []
        key = str(random.randint(1, 99999999))
        for node in self.listed_documents:
            try:
                if node['node_type'] == node_type:
                    existing_keys.append(node['ged_id'].replace('@', '').replace('I', '').replace('F', ''))

            except Exception as e:
                print('Exception in listing ged ids, ' + str(e))

        while key in existing_keys:
            key = str(random.randint(1, 99999999))

        if node_type == 'family':
            return '@F' + key + '@'

        if node_type == 'person':
            return '@I' + key + '@'

    def from_file_to_list_of_dict(self, file: Path):
        first_line = False
        self.file = file
        with open(self.file, 'r') as f:
            for line in f.read().split('\n'):
                decomposed_line = line.split(' ')
                if len(decomposed_line) in [0, 1]:
                    continue
                # handling utf-8 mess
                if first_line is False:
                    first_line = True
                    if decomposed_line[0] == '\ufeff0':
                        decomposed_line[0] = '0'
                    previous_line_level = [decomposed_line[0], decomposed_line[1]]

                self.__previous_document__ = self.__current_document__
                status_file = self.__handle_new_document__(decomposed_line=decomposed_line)

                if status_file == 'in section':
                    # new section
                    if (
                            previous_line_level[0] == '1'
                            or previous_line_level[0] == '0'
                            or previous_line_level[0] == '2'
                    )\
                            and decomposed_line[0] == '1':

                        if decomposed_line[1] == 'NAME':
                            self.__current_document__['name'] = {}
                            self.__current_document__['name']['given_names'] = line[
                                                                              line.find('NAME') + 4:line.find('/')
                                                                              ].split()

                            self.__current_document__['name']['family_name'] = line[line.find('/'):].replace(
                                                                                                             '/', ''
                                                                                                            )

                        elif decomposed_line[1] == 'SEX':
                            self.__current_document__['sex'] = 'female' if decomposed_line[2] == 'F' else 'male'

                        elif decomposed_line[1] == 'NOTE':
                            self.__handle_active_subsection__(self.__sections_lut__[decomposed_line[1]])
                            self.__current_document__[self.__sections_lut__[decomposed_line[1]]] =\
                                line.replace('1 ' + decomposed_line[1] + ' ', '')

                        elif decomposed_line[1] in ['SOUR']:
                            self.__handle_active_subsection__(self.__sections_lut__[decomposed_line[1]])
                            self.__current_document__[self.__sections_lut__[decomposed_line[1]]] = {
                                'name': line.replace('1 ' + decomposed_line[1], '')
                            }

                        elif decomposed_line[1] in ['SUBM']:
                            self.__handle_active_subsection__(self.__sections_lut__[decomposed_line[1]])
                            self.__current_document__[self.__sections_lut__[decomposed_line[1]]] \
                                = line.replace('1 ' + decomposed_line[1], '')

                        elif decomposed_line[1] in self.__links_lut__:
                            self.__handle_links__(self.__links_lut__[decomposed_line[1]], decomposed_line[2])

                        elif decomposed_line[1] in ['GEDC']:
                            if self.__sections_lut__[decomposed_line[1]] not in self.__current_document__:
                                self.__current_document__[self.__sections_lut__[decomposed_line[1]]] = {}

                            self.__handle_active_subsection__(self.__sections_lut__[decomposed_line[1]])

                        elif decomposed_line[1] in ['BIRT', 'DEAT', 'MARR']:
                            self.__handle_active_subsection__(self.__sections_lut__[decomposed_line[1]])

                    if self.__subsection__ in ['birth', 'death', 'marriage'] and decomposed_line[0] == '2':
                        self.__handle_date_place__(event_type=self.__subsection__,
                                                   line_decomposed=decomposed_line,
                                                   line_raw=line)

                    if self.__subsection__ == 'note' and decomposed_line[0] == '2' and decomposed_line[1] == 'CONT':
                        self.__current_document__['note'] = self.__current_document__['note'] \
                                                            + ' ' + line.replace('2 CONT ', '')

                    if self.__subsection__ in ['source', 'gedc'] and decomposed_line[0] == '2'\
                            and decomposed_line[1] in ['VERS', 'NAME', 'CORP', 'FORM']:
                        self.__current_document__[self.__subsection__][self.__sections_lut__[decomposed_line[1]]] =\
                            decomposed_line[2]

                if status_file != 'end of file':
                    previous_line_level = [decomposed_line[0], decomposed_line[1]]

    def add_persons(self, persons: [Person]):
        persons_documents = []
        for person in persons:
            person_document = {
                'node_type': 'person',
                'ged_id': self.__get_unique_ged_id__('person'),
                'name': {'given_names': person.given_names, 'family_name': person.family_name},
                'sex': person.sex,
                'birth': {'date_info': {'date': person.birth_date, 'date_type': person.date_type_birth}},
                'death': {'date_info': {'date': person.death_date, 'date_type': person.date_type_death}},
                'note': person.note,
                'fams': person.fams,
                'famc': person.famc
            }

            self.listed_documents.append(person_document)
            persons_documents.append(person_document)

        return persons_documents

    def add_families(self, families: [Family]):
        families_documents = []
        for family in families:
            family_document = {
                'node_type': 'family',
                'ged_id': self.__get_unique_ged_id__('family'),
                'husband': family.husband,
                'wife': family.wife,
                'children': family.children,
                'marriage': {'date_info': {'date': family.marriage_date, 'date_type': family.date_type_marriage}}
            }

            self.listed_documents.append(family_document)
            families_documents.append(family_document)

        return families_documents

    def load_ged_listed_dict(self, ged_listed_dict: [dict]):
        self.listed_documents = ged_listed_dict

    def from_file_to_list_of_dict_with_cleanup(self, file: UploadFile, path: str = ""):
        contents = file.file.read()
        with open(path + file.filename, 'wb') as f:
            f.write(contents)
        self.from_file_to_list_of_dict(file=path + file.filename)
        rem_file = Path(path + file.filename)
        rem_file.unlink()
