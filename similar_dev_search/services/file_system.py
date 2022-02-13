import json
import os
from pathlib import Path
from typing import Iterator

from github import Repository

from similar_dev_search.data.models import File


class JsonService:
    @staticmethod
    def export_to_json(path: str, repository_name: str, repository: Repository) -> None:
        """
        Export a repository object to a file with json format.

        :param path: The path to the file.
        :param repository_name: The name of the repository.
        :param repository: The repository object.
        """
        directory = Path(path).resolve()
        directory.mkdir(parents=True, exist_ok=True)
        with open((directory / repository_name).__str__() + ".json", "w") as f:
            json_data = json.dumps(repository, indent=2, default=lambda x: x.__dict__)
            f.write(json_data)

    @staticmethod
    def get_from_json(paths: [str]) -> list:
        """
        Extract all json data from a file list.

        :param paths: The json file list.
        :return: Extracted json data.
        """
        repositories = []
        for p in paths:
            path = Path(p).resolve().__str__()
            with open(path, "r") as f:
                repository = json.loads(f.read())
                repositories.append(repository)
        return repositories

    @staticmethod
    def absolute_file_paths(directory: str):
        """
        Get absolute file paths in a directory.

        :param directory: The directory to search all file paths.
        :return: Absolute file paths.
        """
        for dirpath, _, filenames in os.walk(directory):
            for f in filenames:
                yield os.path.abspath(os.path.join(dirpath, f))


class FileSystemService:
    @staticmethod
    def get_files(path: str) -> Iterator[File]:
        """
        Get all files in directory.

        :param path: The directory to search all files.
        :return: Files.
        """
        for root, dirs, files in os.walk(path):
            for name in files:
                yield File(name, root)

    @staticmethod
    def get_file_content(file_path):
        with open(file_path) as f:
            return f.read()

    @staticmethod
    def get_file_count(path):
        try:
            _, _, files = next(os.walk(path))
            return len(files)
        except StopIteration:
            return 0
