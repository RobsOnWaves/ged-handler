from pathlib import Path


class GedFileHandler:
    def __init__(self, file: Path):
        self.file = file
        self.current_document = {}

    def get_filename(self):
        self.file.name

    def __handle_new_document__(self, decomposed_line: [str]):
        # Starting a new section ?
        if decomposed_line[0] == '0':
            if decomposed_line[1] == 'HEAD':
                self.current_document = {'node_type': 'head'}
            if decomposed_line[1] == 'TRLR':
                return
            else:
                try:
                    if decomposed_line[2] == 'INDI':
                        self.current_document = {'node_type': 'person'}
                    elif decomposed_line[2] == 'FAM':
                        self.current_document = {'node_type': 'family'}
                    elif decomposed_line[2] == 'SUBM':
                        self.current_document = {'node_type': 'subm'}

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

                self.__handle_new_document__(decomposed_line=decomposed_line)
                print(decomposed_line)
                print(self.current_document)



