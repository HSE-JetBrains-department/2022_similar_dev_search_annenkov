class Blame:
    def __init__(self, author_name: str, author_email: str, commit: str, lines: [str]) -> None:
        self.author_name = author_name
        self.author_email = author_email
        self.commit = commit
        self.lines = lines


class LineOfCode:
    def __init__(self, number: int, author: str, text: str) -> None:
        self.number = number
        self.author = author
        self.text = text


class File:
    def __init__(self, name: str, path: str, language: str = None, line_authors: [LineOfCode] = None) -> None:
        self.name = name
        self.path = path
        self.name_with_path = path + '/' + name
        self.language = language
        self.line_authors = line_authors


class Change:
    def __init__(self, file_name: str, deletions: [int], additions: [int]) -> None:
        self.file_name = file_name
        self.deletions = deletions
        self.additions = additions


class Commit:
    def __init__(self, parent: bytes, changes: [Change]) -> None:
        self.parent = str(parent)
        self.changes = changes


class Repository:
    def __init__(self, commits: [Commit]) -> None:
        self.commits = commits


class User:
    def __init__(self, languages: {str: int}, var_names: {str: int}) -> None:
        self.languages = languages
        self.var_names = var_names
