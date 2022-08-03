from pathlib import Path


class GedFileHandler:
    def __init__(self, file: Path):
        self.file = file

    def get_filename(self):
        self.file.name

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

                #Starting a new section ?
                if decomposed_line[0] == '0':
                    if decomposed_line[1] == 'HEAD':
                        current_document = {'node_type': 'head'}
                    if  decomposed_line[1] == 'TRLR':
                        #end of file
                        break
                    else:
                        try:
                            if decomposed_line[2] == 'INDI':
                                current_document = {'node_type': 'person'}
                            elif decomposed_line[2] == 'FAM':
                                current_document = {'node_type': 'family'}
                            elif decomposed_line[2] == 'SUBM':
                                current_document = {'node_type': 'subm'}

                        except Exception as e:
                            print('error in parsing levels 0:' + str(e))

                print(decomposed_line)
                print(current_document)



