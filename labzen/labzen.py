import os
from pathlib import Path
import pandas as pd
import numpy as np
from nbformat import read, NO_CONVERT
import re
import glob


def parse_lab(notebook=None):

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

    # If the user did not define the specific file, recursively
    # search for rmd and ipynb files in the working directory
    if notebook is None:
        directory = os.getcwd()
        types = ["*.ipynb", "*.Rmd"]
        files = []
        for type in types:
            pathname = directory + "/**/*" + type
            type_files = glob.glob(pathname, recursive=True)
            files += type_files
        names = [
            str(n + 1) + "." + os.path.basename(file) for n, file in enumerate(files)
        ]
        print("The existing files are:")
        for item in names:
            print(item)
        notebook = input(f"Enter your file number from the above list:")
        notebook = files[int(notebook) - 1]
    path = Path(notebook)
    name, extension = os.path.splitext(notebook)

    # defensive tests
    if extension != ".Rmd" and extension != ".ipynb":
        raise Exception(
            "Sorry, you have not provided Rmarkdown or jupyter notebook file"
        )

    if not isinstance(notebook, str):
        raise Exception("The file path should be string")

    # Parse the markdown contents of rmd or ipynb file
    source = []
    if extension == ".Rmd":
        text_and_code = path.read_text()
        text_and_code = text_and_code.split("```")

        code_blocks = []
        for string in text_and_code:
            if string.startswith("{r"):
                code_blocks.append(string)
            elif string.startswith("{python"):
                code_blocks.append(string)
            else:
                source.append(string)
    else:
        with open(notebook, encoding="utf8") as file:
            notebook = read(file, NO_CONVERT)
            cells = notebook["cells"]
            code_cells = [c for c in cells if c["cell_type"] == "markdown"]
            for cell in code_cells:
                source.append(cell["source"])

    return source


def count_points(file_name: str = None, margins: bool = True):
    """Tally Available Points in Lab

    Args:
        file_name (str): A path or list of paths to MDS lab files (either
            .ipynb or .Rmd). If left blank, the function will recursively
            search for all labs in the working directory based on the file
            extension.
        margins (bool): A boolean indicating whether to add a row for the
            total number of points (optional + required). Defaults to True.

    Returns:
        (pandas.core.frame.DataFrame, pandas.core.frame.DataFrame):
            A tuple of DataFrames. The first is a section-by-section overview
            of points available. The second is a cross table summarising the
            number of optional, required, and total points per lab.

    Example:
        # Navigate to an MDS lab directory and run:
        df, tab = count_points()
        print(df)
        print(tab)
    """
    # Parse a lab file into its markdown blocks
    res = parse_lab(file_name)
    df = pd.DataFrame({"block": np.arange(1, len(res) + 1), "txt": res})

    # Tidy breaks, new lines, extra spaces, and make each line a row
    df["txt"] = df["txt"].str.replace("<br>", "\n")
    df["txt"] = df["txt"].str.split("\n")
    df = df.explode("txt")
    df["txt"] = df["txt"].replace(["", "<hr>"], np.nan)
    df = df.dropna()
    df["txt"] = df["txt"].str.strip()

    # Add variable transformations
    df["header"] = df["txt"].shift(1)
    df["rubric"] = df["txt"].str.contains(r"^rubric\=\{")
    df["below_header"] = df["header"].str.contains(r"^[#]{1,6}\s")
    df["optional"] = df["header"].str.contains("optional|bonus", case=False)

    # Subset to lines containing rubrics only
    df = df.dropna().query("rubric")

    # Extract and sum points
    df["points"] = df["txt"].str.findall(r"(\d+)")
    df2 = df.explode("points")
    df2["points"] = df2["points"].astype(int)
    df["points"] = df2["points"].groupby(df2.index).apply(list)
    df["total"] = df["points"].apply(sum)

    # defensive check
    if not all(df["below_header"]):
        raise Exception(
            "There is a problem parsing this lab. Expecting a rubric tag to "
            + "below a markdown header."
        )

    # Tidy and make the result more human-readable
    booldict = {True: "Optional", False: "Non-Optional"}
    df["type"] = df["optional"].replace(booldict)
    df = df.drop(columns=["rubric", "below_header", "optional"])
    df = df.reset_index(drop=True)
    df["header"] = df["header"].str.replace(r"(^[#]+\s+)", "", regex=True)

    # Generate crosstab
    tab = df.pivot_table("total", "type", aggfunc=sum, margins=margins)
    tab = tab.reset_index()
    one_pt_worth = 0.95 / tab.loc[tab["type"] == "Non-Optional", "total"]
    tab["prop"] = tab["total"] * one_pt_worth[0]

    # add percent to full table
    df["prop"] = df["total"] * one_pt_worth[0]

    # simplify rubric names
    df["rubric"] = df["txt"].str.findall(r"([a-z]+)(?=\:\d)")

    # re-order columns
    df = df[["block", "header", "rubric", "points", "total", "prop", "type"]]

    return df, tab


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


def check_mechanics(file_name: str):
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
