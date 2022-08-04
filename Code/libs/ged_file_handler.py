from pathlib import Path

class GedFileHandler:
    def __init__(self, file: Path):
        self.file = file
        self.__current_document__ = {}

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

    def to_dict(self):
        first_line = False
        with open(self.file, 'r') as f:
            for line in f.read().split('\n'):
                print(line)
                decomposed_line = line.split(' ')

                #handling utf-8 mess
                if first_line is False:
                    first_line = True
                    if decomposed_line[0] == '\ufeff0':
                        decomposed_line[0] = '0'
                    previous_line_level = [decomposed_line[0], decomposed_line[1]]

                self.__handle_new_document__(decomposed_line=decomposed_line)
                if decomposed_line[0] != '0':
                    if (previous_line_level[0] == '1' or previous_line_level[0] == '0') and decomposed_line[0] == '1': #new subsection
                        if len(decomposed_line) > 2:
                            if decomposed_line[1] == 'NAME':


                                self.__current_document__.update({'name':
                                                                      {'given_names': line[line.find('NAME')+4:line.find('/')].split(),
                                                                       'family_name': line[line.find('/'):].replace('/','')
                                                                       }
                                                                  })
                            if decomposed_line[1] == 'SEX':
                                self.__current_document__.update({'sex':
                                                                      'female' if decomposed_line[2] == 'F' else 'male'
                                                                  })

                print(decomposed_line)

                print(self.__current_document__)

                previous_line_level = [decomposed_line[0], decomposed_line[1]]



