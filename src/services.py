import json
import os
from pathlib import Path

from git import Repo, GitCommandError
from github import Github

from src.constants import VENDOR_PATH
from src.models import Repository, LineOfCode, File


class GitService:
    def __init__(self) -> None:
        pass

    def clone_repo(self, clone_url: str, path: str, verbose: bool = False) -> None:
        try:
            if verbose:
                print('Starting repository cloning')
            Repo.clone_from(clone_url, path)
            if verbose:
                print('Repository cloning done')
        except GitCommandError:
            if verbose:
                print('Repository already exists')

    def get_blame(self, file: str, repo_path: str) -> [LineOfCode]:
        try:
            repo = Repo(repo_path)
            lines_of_code = []
            for commit, lines in repo.blame('HEAD', file):
                for line in lines:
                    lines_of_code.append(LineOfCode(len(lines_of_code), commit.author.name, line))
            return lines_of_code
        except GitCommandError:
            return []


class GithubService:
    def __init__(self) -> None:
        self.token = os.environ['GITHUB_API_KEY']
        self.g = Github(self.token)

    def get_repos(self, username: str) -> [Repository]:
        return self.g.get_user(username).get_repos()

    def get_repo(self, username: str, repo_name: str) -> Repository:
        return self.g.get_user(username).get_repo(repo_name)


class JsonService:
    def __init__(self) -> None:
        pass

    @staticmethod
    def export_to_json(repository_name: str, repository_files: [File]) -> None:
        directory = Path(VENDOR_PATH + '/jsons/').resolve().__str__()
        Path(directory).mkdir(parents=True, exist_ok=True)
        with open(directory + '/' + repository_name + '.json', 'w') as f:
            json_data = json.dumps(repository_files, indent=1, default=lambda x: x.__dict__)
            f.write(json_data)
