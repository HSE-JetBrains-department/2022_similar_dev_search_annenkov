from pandas import DataFrame

from similar_dev_search.services.file_system import JsonService
from similar_dev_search.services.user_vectors import UserVectorService


def get_user_vectors_dataframe(jsons_path: str) -> DataFrame:
    """
    Calculate user vectors for all users and return DataFrame with user vectors.

    :param jsons_path: Path to json files.
    :return: Dataframe.
    """
    paths = JsonService.absolute_file_paths(jsons_path)
    repositories = JsonService.get_from_json(paths)
    user_vector_service = UserVectorService()
    users_dict = user_vector_service.get_users_dict(repositories)
    dataframe = user_vector_service.get_users_pandas(users_dict)
    del users_dict
    return dataframe
