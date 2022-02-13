from io import BytesIO, StringIO

import enry
from dulwich import repo, patch
from tree_sitter import Parser, Tree
from unidiff import PatchSet, UnidiffParseError, PatchedFile

from src.constants import languages
from src.helpers import FileSystemHelper
from src.models import Change, Repository, Commit, File
from src.services import GitService
from src.setup import build_tree_sitter


class LanguagesProvider:
    def __init__(self, repository_path: str) -> None:
        self.repository_path = repository_path
        self.languages_counts = {}
        self.files_with_languages = []

    def add_language(self, language: str) -> None:
        if language not in self.languages_counts.keys():
            self.languages_counts[language] = 1
        else:
            self.languages_counts[language] += 1

    def add_file(self, file: File, language: str) -> None:
        file_with_language = File(
            name=file.name,
            path=file.path,
            language=language)
        self.files_with_languages.append(file_with_language)

    def get_language(self, file_name: str, content: str) -> str:
        language = enry.get_language(file_name, str.encode(content))
        if language == '':
            return 'Other'
        return language

    def calc_languages(self) -> None:
        for file in FileSystemHelper.get_files(self.repository_path):
            with open(file.name_with_path) as f:
                try:
                    language = self.get_language(file.name, f.read())
                    self.add_language(language)
                    self.add_file(file, language)
                except UnicodeDecodeError:
                    pass

    def get_language_ratio(self) -> {str: float}:
        return {k: self.languages_counts[k] / sum(self.languages_counts[k] for k in self.languages_counts) for k in
                self.languages_counts}


class CodeEntitiesProvider:
    def __init__(self, language: str, git_service: GitService) -> None:
        build_tree_sitter(git_service)
        self.parser = Parser()
        self.parser.set_language(languages[language])

    def get_tree(self, lines_of_code: str) -> Tree:
        return self.parser.parse(bytes(lines_of_code, 'utf-8'))


class RepositoryProvider:
    def __init__(self, path: str) -> None:
        self.path = path
        self.r = repo.Repo(self.path)
        self.commits = {}
        for entry in self.r.get_walker():
            self.commits[entry.commit.id] = entry.commit

    def get_commit_raw_diff(self, commit_id: bytes) -> str:
        out = BytesIO()
        patch.write_tree_diff(
            out,
            self.r.object_store,
            self.commits[self.commits[commit_id].parents[0]].tree,
            self.commits[commit_id].tree)
        return out.getvalue().decode('ascii')

    def get_file(self, patched_file: PatchedFile) -> Change:
        file_path = patched_file.path  # file name
        del_line_no = [
            line.target_line_no
            for hunk in patched_file for line in hunk
            if line.is_added and line.value.strip() != '']  # the row number of deleted lines
        ad_line_no = [
            line.source_line_no
            for hunk in patched_file for line in hunk
            if line.is_removed and line.value.strip() != '']  # the row number of added liens
        return Change(file_path, del_line_no, ad_line_no)

    def get_commit_diff_object(self, commit_id: bytes) -> [Change]:
        try:
            s = self.get_commit_raw_diff(commit_id)
            patch_set = PatchSet(StringIO(s))
            change_list = []
            for patched_file in patch_set:
                change_list.append(self.get_file(patched_file))
            return change_list
        except (UnicodeDecodeError, UnidiffParseError):
            return []
        except Exception:
            return []

    def get_repository(self) -> Repository:
        result_commits = []
        for key in self.commits.keys():
            try:
                changes = self.get_commit_diff_object(key)
                commit = Commit(self.commits[key].parents[0], changes)
                result_commits.append(commit)
            except IndexError:
                return None
        return Repository(result_commits)
