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

    def __handle_date_place__(self, event_type: str, line_decomposed: [str], line_raw: str):
        if line_decomposed[1] == 'DATE':
            # Initiating the event
            self.__current_document__[event_type] = {}
            self.__current_document__[event_type]['date_info'] = {}

            if len(line_decomposed) == 5:  # full date

                self.__current_document__[event_type]['date_info']['date'] = date.fromisoformat(line_decomposed[4]
                                                                                                + '-' +
                                                                                                month_lut.get(
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
                                                                                                month_lut[
                                                                                                    line_decomposed[2]]
                                                                                                + '-01')
                self.__current_document__[event_type]['date_info']['date_type'] = 'year_month_only'

            else:
                raise Exception('unhandled date line' + line_decomposed)

        if line_decomposed[1] == 'PLAC':
            try:
                self.__current_document__[event_type]['place'] = line_raw.replace('2 PLAC ', '')

            except Exception as e:
                print('Exception adding a place to the current entry:' + str(e))

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
                            self.__handle_active_subsection__('note')
                            self.__current_document__['note'] = line.replace('1 NOTE ', '')

                        elif decomposed_line[1] == 'BIRT':
                            self.__handle_active_subsection__('birth')

                        elif decomposed_line[1] == 'DEAT':
                            self.__handle_active_subsection__('death')

                    if self.__subsection__ == 'birth' and decomposed_line[0] == '2':
                        self.__handle_date_place__('birth', decomposed_line, line)

                    if self.__subsection__ == 'death' and decomposed_line[0] == '2':
                        self.__handle_date_place__('death', decomposed_line, line)

                    if self.__subsection__ == 'note' and decomposed_line[0] == '2' and decomposed_line[1] == 'CONT':
                        self.__current_document__['note'] = self.__current_document__['note'] \
                                                            + ' ' + line.replace('2 CONT ', '')

                print(decomposed_line)

                print(self.__current_document__)

                previous_line_level = [decomposed_line[0], decomposed_line[1]]
