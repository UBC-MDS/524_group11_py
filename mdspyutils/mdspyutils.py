import pandas as pd


def parse_lab(file_name: str) -> list:
    """[summary]

    Args:
        file_name (str): [description]

    Returns:
        list: [description]
    """
    return None


def count_points(file_name: str = None) -> pd.DataFrame:
    """Tally Available Points in Lab

    Args:
        file_name (str): A path or list of paths to MDS lab files (either
            .ipynb or .Rmd). If left blank, the function will recursively
            search for all labs in the working directory based on the file
            extension.

    Returns:
        pd.DataFrame: A cross table summarising the number of optional,
            required, and total points per lab.

    Example:
        count_points()
    """
    return None


def check_mechanics(file_name: str) -> bool:
    """[summary]

    Args:
        file_name (str): [description]

    Returns:
        bool: [description]
    """
    return None