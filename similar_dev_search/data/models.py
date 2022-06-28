from pathlib import Path


class LineOfCode:
    def __init__(self, number: int, author: str, text: str) -> None:
        self.number = number
        self.author = author
        self.text = text


class File:
    def __init__(self, name: str, path: str, language: str = None, line_authors: [LineOfCode] = None) -> None:
        self.name = name
        self.path = path
        self.name_with_path = Path(path).resolve() / name
        self.language = language
        self.line_authors = line_authors


class Change:
    def __init__(self, file_name: str, language: str, deletions: [int], additions: [int], variable_names: [str],
                 import_names: [str]) -> None:
        self.file_name = file_name
        self.language = language
        self.deletions = deletions
        self.additions = additions
        self.variable_names = variable_names
        self.import_names = import_names


class Commit:
    def __init__(self, author: bytes, parent: bytes, changes: [Change]) -> None:
        self.author = author.decode()
        self.parent = str(parent)
        self.changes = changes


class Repository:
    def __init__(self, commits: [Commit]) -> None:
        self.commits = commits


class User:
    def __init__(self, languages: {str: int}, var_names: {str: int}) -> None:
        self.languages = languages
        self.var_names = var_names
