from io import BytesIO, StringIO
import os
import pathlib

from dulwich import patch, repo
from git import GitCommandError, Repo
import github
from github import Github, NamedUser
from unidiff import PatchSet, PatchedFile, UnidiffParseError

from similar_dev_search.data.models import Change, Commit, Repository
from similar_dev_search.services import code_parser
from similar_dev_search.services.code_parser import LanguagesProvider
from similar_dev_search.services.file_system import FileSystemService


class GitService:
    @staticmethod
    def clone_repo(clone_url: str, path: str, verbose: bool = False) -> None:
        try:
            if verbose:
                print("Starting repository cloning")
            Repo.clone_from(clone_url, path)
            if verbose:
                print("Repository cloning done")
        except GitCommandError:
            if verbose:
                print("Repository already exists")


class GithubService:
    def __init__(self) -> None:
        self.token = os.environ["GITHUB_API_KEY"]
        self.github = Github(self.token)

    def get_user(self, username: str) -> NamedUser:
        return self.github.get_user(username)

    def get_repos(self, username: str) -> [github.Repository]:
        return self.github.get_user(username).get_repos()

    def get_repo(self, username: str, repo_name: str) -> github.Repository:
        return self.github.get_user(username).get_repo(repo_name)


class RepositoryProvider:
    def __init__(self, path: str) -> None:
        self.path = path
        self.r = repo.Repo(self.path)
        self.commits = {}
        self.result_commits = []
        for entry in self.r.get_walker():
            self.commits[entry.commit.id] = entry.commit

    def get_commit_raw_diff(self, commit_id: bytes) -> str:
        """
        Get a raw diff of a commit.

        :param commit_id: Id of the commit.
        :return: The raw diff.
        """
        out = BytesIO()
        patch.write_tree_diff(
            out,
            self.r.object_store,
            self.commits[self.commits[commit_id].parents[0]].tree,
            self.commits[commit_id].tree)
        return out.getvalue().decode("utf-8")

    def get_file(self, patched_file: PatchedFile, tree_sitter_build_path: str) -> Change:
        """
        Get a changes block of the commit.

        :param patched_file: The file to search changes.
        :return: The changes block.
        """
        file_path = patched_file.path  # file name
        del_line_no = [
            line.target_line_no
            for hunk in patched_file for line in hunk
            if line.is_added and line.value.strip() != ""]  # the row number of deleted lines
        ad_line_no = [
            line.source_line_no
            for hunk in patched_file for line in hunk
            if line.is_removed and line.value.strip() != ""]  # the row number of added liens
        file_content = FileSystemService.get_file_content(
            str(pathlib.Path().resolve() / self.path / patched_file.path))
        language = LanguagesProvider().get_language(
            patched_file.path, str(pathlib.Path().resolve() / self.path / patched_file.path)
        )
        code_entities = code_parser.CodeEntitiesParser.parse_file([language], file_content, tree_sitter_build_path)
        return Change(file_path, language, len(del_line_no), len(ad_line_no), code_entities["names"],
                      code_entities["imports"])

    def get_commit_diff_object(self, commit_id: bytes, tree_sitter_build_path: str) -> [Change]:
        """
        Get all differences in the commit.

        :param commit_id: Id of the commit.
        :return: All differences.
        """
        try:
            s = self.get_commit_raw_diff(commit_id)
            patch_set = PatchSet(StringIO(s))
            change_list = []
            for patched_file in patch_set:
                change_list.append(self.get_file(patched_file, tree_sitter_build_path))
            return change_list
        except (UnicodeDecodeError, UnidiffParseError):
            return []
        except Exception:
            return []

    def get_repository(self, tree_sitter_build_path: str) -> Repository:
        """
        Get a repository object.

        :return: The repository object.
        """
        result_commits = []
        for key in self.commits.keys():
            try:
                if len(self.commits[key].parents) == 1:
                    changes = self.get_commit_diff_object(key, tree_sitter_build_path)
                    commit = Commit(self.commits[key].author, self.commits[key].parents[0], changes)
                    result_commits.append(commit)
            except IndexError:
                pass
        return Repository(result_commits)
