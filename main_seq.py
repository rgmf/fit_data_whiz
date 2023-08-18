import os

from .parse import FitActivityParser


if __name__ == "__main__":
    fit_parse = FitActivityParser()
    folder_files: str = "pyfittest/tests/files"

    def parse(path_file: str) -> None:
        fit_parse.parse(path_file)

    for _ in range(25):
        for file in os.listdir(folder_files):
            path_file = os.path.join(folder_files, file)
            if not os.path.isfile(path_file):
                continue

            fit_parse.parse(path_file)
