from pathlib import Path


class GedFileHandler:
    def __init__(self, file: Path):
        self.file = file

    def get_filename(self):
        self.file.name

    def to_dict(self):
        with open(self.file, 'r') as f:
            for line in f.read().split('\n'):
                print(line)
