import os
from pathlib import Path
import pandas as pd
import numpy as np


def parse_lab(file_name: str) -> list:
    """Parse MDS lab files to return the markdown content

    Args:
        file_name (str): A path or list of paths to MDS lab files (either
            .ipynb or .Rmd). If left blank, the function will recursively
            search for all labs in the working directory based on the file
            extension.
    Returns:
        list: Each element of list is a content of one markdown cell.

    Example:
        parse_lab()
    """
    return None


def count_points(file_name: str = None) -> pd.DataFrame:

def count_points(file_name: str = None, margins: bool = True) -> pd.DataFrame:
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
    # Calculate a summary table of points per section
    res = parse_lab(file_name)
    df = pd.DataFrame({"block": np.arange(1, len(res) + 1), "txt": res})
    df["txt"] = df["txt"].str.replace("<br>", "\n")
    df["txt"] = df["txt"].str.split("\n")
    df = df.explode("txt")
    df["txt"] = df["txt"].replace(["", "<hr>"], np.nan)
    df = df.dropna()
    df["txt"] = df["txt"].str.strip()
    df["header"] = df["txt"].shift(1)
    df["rubric"] = df["txt"].str.contains(r"^rubric\=\{")
    df["below_header"] = df["header"].str.contains(r"^[#]{1,6}\s")
    df["optional"] = df["header"].str.contains("optional|bonus", case=False)
    df = df.dropna().query("rubric")
    df["points"] = df["txt"].str.findall(r"(\d+)")
    df2 = df.explode("points")
    df2["points"] = df2["points"].astype(int)
    df["points"] = df2["points"].groupby(df2.index).apply(list)
    df["total"] = df["points"].apply(sum)
    booldict = {True: "Optional", False: "Non-Optional"}
    df["type"] = df["optional"].replace(booldict)
    df.drop(columns=["rubric", "below_header", "optional"])
    df = df.reset_index(drop=True)

    # Generate crosstab
    tab = df.pivot_table("total", "type", aggfunc=sum, margins=margins).reset_index()
    return tab


def check_repo_link(file_name: str) -> bool:
    """Check whether the user has included the github repo link in his/her
        repository

    Args:
        file_name (str): A path or list of paths to MDS lab files (either
            .ipynb or .Rmd). If left blank, the function will recursively
            search for all labs in the working directory based on the file
            extension.

    Returns:
        bool: a boolean output

    Example:
        check_repo_link()
    """
    return None


def check_lat_version(file_name: str) -> bool:
    """Check whether the user has pushed the latest version in his/her
        repository

    Args:
        file_name (str): A path or list of paths to MDS lab files (either
            .ipynb or .Rmd). If left blank, the function will recursively
            search for all labs in the working directory based on the file
            extension.

    Returns:
        bool: a boolean output

    Example:
        check_lat_version()
    """
    return None


def check_commits(file_name: str) -> bool:
    """Check whether the user has at least three commits

    Args:
        file_name (str): A path or list of paths to MDS lab files (either
            .ipynb or .Rmd). If left blank, the function will recursively
            search for all labs in the working directory based on the file
            extension.

    Returns:
        bool: a boolean output

    Example:
        check_commits()
    """
    return None


def check_mechanics(file_name: str) -> NoneType:
    """Performs Mechanics Checks on a MDS Lab
       This function check that you have a Github repo link, that you have
       pushed your latest commit, and that you have at least three commit
       messages authored by you in your history.

    Args:
        file_name (str): A path or list of paths to MDS lab files (either
            .ipynb or .Rmd). If left blank, the function will recursively
            search for all labs in the working directory based on the file
            extension.

    Returns:
        NoneType: The function prints the results of the mechanics checks to screen

    Example:
        check_mechanics()

    """
    return None

  
