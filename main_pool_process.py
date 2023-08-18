import os
from concurrent.futures import ProcessPoolExecutor

from .parse import FitActivityParser


if __name__ == "__main__":
    fit_parse = FitActivityParser()
    folder_files: str = "pyfittest/tests/files"

    def parse(path_file: str) -> None:
        global fit_parse
        fit_parse.parse(path_file)

    cpu_count: int | None = os.cpu_count()
    num_process: int = 4 if cpu_count is None else cpu_count // 2
    with ProcessPoolExecutor(num_process) as ppe:
        for _ in range(25):
            for file in os.listdir(folder_files):
                path_file = os.path.join(folder_files, file)
                if not os.path.isfile(path_file):
                    continue

                ppe.submit(parse, path_file)
