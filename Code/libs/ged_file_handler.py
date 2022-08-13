from pathlib import Path
from datetime import date

month_lut = {
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


class GedFileHandler:
    def __init__(self, file: Path):
        self.file = file
        self.__current_document__ = {}
        self.__subsection__ = str

    def get_filename(self):
        return self.file.name

    def __handle_new_document__(self, decomposed_line: [str]):
        # Starting a new section ?
        if decomposed_line[0] == '0':
            if decomposed_line[1] == 'HEAD':
                self.__current_document__ = {'node_type': 'head'}
            elif decomposed_line[1] == 'TRLR':
                return
            else:
                try:
                    if decomposed_line[2] == 'INDI':
                        self.__current_document__ = {'node_type': 'person', 'ged_id': decomposed_line[1]}
                    elif decomposed_line[2] == 'FAM':
                        self.__current_document__ = {'node_type': 'family', 'ged_id': decomposed_line[1]}
                    elif decomposed_line[2] == 'SUBM':
                        self.__current_document__ = {'node_type': 'subm'}

                except Exception as e:
                    print('error in parsing levels 0:' + str(e))

    def __handle_active_subsection__(self, subsection: str):
        self.__subsection__ = subsection

    def to_dict(self):
        first_line = False
        with open(self.file, 'r') as f:
            for line in f.read().split('\n'):
                print(line)
                decomposed_line = line.split(' ')

                # handling utf-8 mess
                if first_line is False:
                    first_line = True
                    if decomposed_line[0] == '\ufeff0':
                        decomposed_line[0] = '0'
                    previous_line_level = [decomposed_line[0], decomposed_line[1]]

                self.__handle_new_document__(decomposed_line=decomposed_line)
                if decomposed_line[0] != '0':
                    # new section
                    if (previous_line_level[0] == '1' or previous_line_level[0] == '0') and decomposed_line[0] == '1':
                        if len(decomposed_line) > 2:
                            if decomposed_line[1] == 'NAME':
                                self.__current_document__.update({'name':
                                                                  {'given_names': line[
                                                                                  line.find('NAME') + 4:line.find('/')
                                                                                  ].split(),
                                                                   'family_name': line[line.find('/'):].replace('/', '')
                                                                   }
                                                                  })
                            if decomposed_line[1] == 'SEX':
                                self.__current_document__.update({'sex':
                                                                 'female' if decomposed_line[2] == 'F' else 'male'}
                                                                 )
                        elif decomposed_line[1] == 'BIRT':
                            self.__handle_active_subsection__('birth')

                    if self.__subsection__ == 'birth' and decomposed_line[0] == '2':
                        if decomposed_line[1] == 'DATE' and len(decomposed_line) == 5:  # full date
                            self.__current_document__.update({'birth_info':
                                                             {'date': date.fromisoformat(decomposed_line[4]
                                                                                         + '-' +
                                                                                         month_lut.get(decomposed_line[3])
                                                                                         + '-' +
                                                                                         (decomposed_line[2] if len(decomposed_line[2]) == 2 else '0' + decomposed_line[2]))}})

                print(decomposed_line)

                print(self.__current_document__)

                previous_line_level = [decomposed_line[0], decomposed_line[1]]
