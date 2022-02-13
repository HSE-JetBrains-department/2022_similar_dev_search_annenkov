from pathlib import Path

from github import Repository

from similar_dev_search.services.file_system import FileSystemService, JsonService
from similar_dev_search.services.git import GitService, GithubService
from similar_dev_search.services.git import RepositoryProvider
from similar_dev_search.services.setup import setup


def find_repos(username: str, repo_name: str, depth: int = 1, max_depth: int = 3, max_top_starred_repos: int = 5,
               max_contributors: int = 10) -> {Repository}:
    """
    Find all repos recursively. Max depth responsible for the number of nested calls.
    Max depth doesn't mean the number of repos, but the number of nested calls.
    Max depth is selected intuitively.

    :param username: Username of the repo author.
    :param repo_name: Name of the repo.
    :param depth: Depth of the search.
    :param max_depth: Max depth of the search.
    :param max_top_starred_repos: Max number of top starred repos.
    :param max_contributors: Max number of contributors.
    :return: Set of all repos.
    """
    ghs = GithubService()
    repo = ghs.get_repo(username, repo_name)
    contributors = repo.get_contributors()
    result = {repo}
    if depth <= max_depth:
        for contributor in contributors[:max_contributors]:
            stars = ghs.get_user(contributor.login).get_starred()
            stars = get_top_starred_repos(stars)[:max_top_starred_repos]
            for star in stars:
                result = result | find_repos(star.owner.login, star.name, depth + 1, max_depth, max_top_starred_repos,
                                             max_contributors)
    return result


def handle_repo(username: str, repo_name: str, repo_path: str, tree_sitter_build_path: str, jsons_path: str) -> None:
    """
    Clone repo and export to json.

    :param username: Username of the repo author.
    :param repo_name: Name of the repo.
    :param repo_path: Path to the repo.
    :param tree_sitter_build_path: Path to the tree-sitter build library.
    :param jsons_path: Path to the json files.
    """
    ghs = GithubService()
    gs = GitService()
    repo = ghs.get_repo(username, repo_name)
    gs.clone_repo(repo.clone_url, repo_path)
    if not Path((Path(jsons_path).resolve() / repo.name).__str__() + ".json").is_file():
        p = RepositoryProvider(repo_path)
        repository = p.get_repository(tree_sitter_build_path)
        JsonService.export_to_json(jsons_path, repo.name, repository)
    print("\r", FileSystemService.get_file_count(jsons_path), "handled repositories...", end='', flush=True)


def get_top_starred_repos(stars: Repository) -> [Repository]:
    stars = list(stars)
    return sorted(stars, key=lambda x: x.stargazers_count, reverse=True)
