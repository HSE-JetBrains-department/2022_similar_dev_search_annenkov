import click
from joblib import Parallel, delayed
from prettytable import PrettyTable

from cli_utils.fetch_repos import find_repos, handle_repo
from cli_utils.get_similar_devs import get_user_vectors_dataframe
from data.constants import BUILD_PATH, JSONS_PATH, N_JOBS, REPOS_PATH
from services.file_system import FileSystemService
from services.user_vectors import UserVectorService
from similar_dev_search.services import setup
from similar_dev_search.services.git import GitService


@click.group()
def cli():
    pass


@cli.command()
@click.option('--username', default='scikit-learn', help='Username for start repo')
@click.option('--reponame', default='scikit-learn', help='Start repo name')
@click.option('--max_repos', default=10, help='Max count of repos')
@click.option('--max_depth', default=2, help='Max depth of the search')
@click.option('--max_top_starred_repos', default=5, help='Max number of top starred repos')
@click.option('--max_contributors', default=3, help='Max number of contributors')
@click.option('--build_path', default=BUILD_PATH, help='Path to the tree-sitter build library')
@click.option('--jsons_path', default=JSONS_PATH, help='Path to the json files')
@click.option('--repos_path', default=REPOS_PATH, help='Path to the repos')
@click.option('--n_jobs', default=N_JOBS, help='Number of jobs')
def fetch_repos(username: str, reponame: str, max_repos: int, max_depth: int, max_top_starred_repos: int,
                max_contributors: int, build_path: str, jsons_path: str, repos_path: str, n_jobs: int) -> None:
    print("Searching repositories...")
    repos_list = list(find_repos(
        username,
        reponame,
        max_depth=max_depth,
        max_top_starred_repos=max_top_starred_repos,
        max_contributors=max_contributors))
    print("Searching done...")
    print("Setup tree-sitter...")
    gs = GitService()
    setup.setup(gs)
    print("Setup done...")
    repositories_count = FileSystemService.get_file_count(jsons_path)
    Parallel(n_jobs=n_jobs)(
        delayed(handle_repo)(
            repo.owner.login,
            repo.name,
            repos_path + repo.name,
            build_path,
            jsons_path)
        for repo in repos_list[:max(0, max_repos - repositories_count + 1)]
    )


@cli.command()
@click.option('--dev_name', default='./', help='Developer name to search similar developers')
@click.option('--jsons_path', default=JSONS_PATH, help='Path to the json files')
@click.option('--max-cosine-similarity-devs', default=7000, help='Max number of developers to count cosine similarity')
def start_search(dev_name: str, jsons_path: str, max_cosine_similarity_devs: int) -> None:
    dataframe = get_user_vectors_dataframe(jsons_path)
    devs = UserVectorService().get_similar_dev(dataframe, dev_name, max_cosine_similarity_devs)
    table = PrettyTable(['Name', 'Similarity'])
    table.align = "r"
    for dev in devs:
        table.add_row([dev[0], dev[1]])
    print(table)


if __name__ == '__main__':
    cli()
