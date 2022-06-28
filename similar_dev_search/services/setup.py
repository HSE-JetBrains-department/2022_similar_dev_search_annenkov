from joblib import Parallel, delayed
from tree_sitter import Language

from similar_dev_search.data.constants import BUILD_PATH, N_JOBS, VENDOR_PATH, language_names
from similar_dev_search.services.git import GitService

languages = {}


def clone_tree_sitter_repo(git_service: GitService, language_name: str) -> None:
    git_service.clone_repo(
        clone_url="https://github.com/tree-sitter/tree-sitter-" + language_name,
        path=VENDOR_PATH + "tree-sitter/tree-sitter-" + language_name)


def build_tree_sitter(git_service: GitService) -> None:
    Parallel(n_jobs=N_JOBS)(
        delayed(clone_tree_sitter_repo)(git_service, language_name) for language_name in language_names
    )
    Language.build_library(
        BUILD_PATH + "my-languages.so",
        [VENDOR_PATH + "tree-sitter/tree-sitter-" + language for language in language_names])
    for language in language_names:
        languages[language] = Language(BUILD_PATH + "my-languages.so", language)


def setup(git_service: GitService):
    build_tree_sitter(git_service)
