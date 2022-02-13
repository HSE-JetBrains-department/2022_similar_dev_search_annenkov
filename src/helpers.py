import os
from typing import Iterator

from src.models import File


class FileSystemHelper:
    @staticmethod
    def get_file(path: str) -> File:
        pass

    @staticmethod
    def get_files(path: str) -> Iterator[File]:
        for root, dirs, files in os.walk(path):
            for name in files:
                yield File(name, root)
