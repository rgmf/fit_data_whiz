import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, Future, as_completed

from .parse import FitActivityParser


if __name__ == "__main__":
    fit_parse = FitActivityParser()
    folder_files: str = "pyfittest/tests/files"

    def parse(path_file: str) -> None:
        global fit_parse
        fit_parse.parse(path_file)

    def parse_files(filepaths: list[str]) -> tuple:
        with ThreadPoolExecutor(len(filepaths)) as executor:
            futures = [executor.submit(parse, path_file) for path_file in filepaths]
            data_list = [future.result() for future in futures]
            return (data_list, filepaths)

    path_files: list[str] = []
    for _ in range(25):
        for file in os.listdir(folder_files):
            path_file = os.path.join(folder_files, file)
            if not os.path.isfile(path_file):
                continue

            path_files.append(path_file)

    n_workers = 8
    chunksize = round(len(path_files) / n_workers)
    with ProcessPoolExecutor(n_workers) as executor:
        futures: list[Future] = list()
        for i in range(0, len(path_files), chunksize):
            filepaths = path_files[i:(i + chunksize)]
            future = executor.submit(parse_files, filepaths)
            futures.append(future)

        for future in as_completed(futures):
            _, filepaths = future.result()
