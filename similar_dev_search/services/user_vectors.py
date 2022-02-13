import numpy
from pandas import DataFrame
import pandas as pd
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import tqdm


class UserVectorService:
    @staticmethod
    def get_users_dict(repositories: list) -> dict:
        """
        Get dict with users, languages, variables, imports.

        :param repositories: Repositories to fetch information.
        :return: Dict with users, languages, variables, imports.
        """
        print("Getting all devs from JSONs...")
        ds = dict()
        for repository in tqdm.tqdm(repositories):
            for commit in repository["commits"]:
                if commit["author"] not in ds:
                    ds[commit["author"]] = dict()
                for change in commit["changes"]:
                    if change["language"] not in ds[commit["author"]]:
                        ds[commit["author"]]["a__" + change["language"]] = 0
                        ds[commit["author"]]["d__" + change["language"]] = 0
                    ds[commit["author"]]["a__" + change["language"]] += change["additions"]
                    ds[commit["author"]]["d__" + change["language"]] += change["deletions"]
                    for variable_name in change["variable_names"]:
                        if variable_name not in ds[commit["author"]]:
                            ds[commit["author"]]["v__" + variable_name] = 0
                        ds[commit["author"]]["v__" + variable_name] += 10
                    for import_name in change["import_names"]:
                        if import_name not in ds[commit["author"]]:
                            ds[commit["author"]]["i__" + import_name] = 0
                        ds[commit["author"]]["i__" + import_name] += 10
        return ds

    @staticmethod
    def get_users_pandas(ds: dict) -> DataFrame:
        print("Building vectorizer...")
        vectorizer = DictVectorizer(dtype=numpy.uint8, sparse=False)
        matrix = vectorizer.fit_transform(ds.values())
        column_labels = vectorizer.get_feature_names()
        print("Building DataFrame...")
        df = pd.DataFrame(matrix, columns=column_labels, index=ds.keys())
        df.fillna(0, inplace=True)
        del ds
        return df

    @staticmethod
    def get_similar_dev(dataframe: DataFrame, name: str, max_cosine_similarity_devs: int) -> list:
        print("Getting similar devs...")
        vector = dataframe.loc[[name]]
        cosine_matrix = cosine_similarity(dataframe.head(max_cosine_similarity_devs), vector)
        result_items = list(dict(zip(list(dataframe.index.values), list(cosine_matrix))).items())
        first_index = 0
        if result_items[0][0] == name:
            first_index = 1
        return sorted(result_items, key=lambda x: x[1], reverse=True)[first_index:20]
