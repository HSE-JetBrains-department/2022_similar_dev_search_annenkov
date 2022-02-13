from git import Repo
from joblib import Parallel, delayed
from tqdm import tqdm

from src.constants import n_jobs, VENDOR_PATH
from src.models import File
from src.providers import LanguagesProvider
from src.services import GitService, GithubService, JsonService
from src.setup import setup


class DeveloperVectorManager:
    """
    A class to manage developer vectors.
    """

    def __init__(
            self,
            git_service: GitService,
            github_service: GithubService,
    ) -> None:
        self.git_service = git_service
        self.github_service = github_service

    def clone_all_user_repos(self, username: str) -> [Repo]:
        repos = list(self.github_service.get_repos(username))
        Parallel(n_jobs=n_jobs)(
            delayed(self.git_service.clone_repo)(repo.clone_url, VENDOR_PATH + 'repos/' + repo.name)
            for repo in tqdm(repos)
        )
        return repos

    def get_repo_files_languages(self, repo_path: str) -> [File]:
        lp = LanguagesProvider(repo_path)
        lp.calc_languages()
        return lp.files_with_languages

    def get_file_authors(self, file: File, repo_path: str) -> File:
        blame = self.git_service.get_blame(file.name_with_path.replace(repo_path + '/', ''), repo_path)
        return File(file.name, file.path, file.language, blame)

    def get_files_authors(self, files: [File], repo_path: str) -> [File]:
        files_with_blames = Parallel(n_jobs=n_jobs)(
            delayed(self.get_file_authors)(file, repo_path)
            for file in files
        )
        return files_with_blames

    def get_code_structure(self) -> None:
        pass
    def calc_user_vector(self, username: str) -> None:
        repos_to_files = {}
        repos = self.clone_all_user_repos(username)
        for repo in tqdm(repos):  # Calc languages
            repos_to_files[repo.name] = self.get_repo_files_languages(VENDOR_PATH + 'repos/' + repo.name)
        for repo in tqdm(repos):  # Calc authors
            repos_to_files[repo.name] = self.get_files_authors(
                repos_to_files[repo.name], VENDOR_PATH + 'repos/' + repo.name)
        for repo in tqdm(repos):  # Export to JSONs
            JsonService.export_to_json(repo.name, repos_to_files[repo.name])


# Just A Temporary Part
gs = GitService()
setup(gs)
ghs = GithubService()
dvm = DeveloperVectorManager(gs, ghs)
dvm.calc_user_vector('Vakosta')
