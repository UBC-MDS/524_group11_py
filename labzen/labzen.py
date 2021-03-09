import os
from pathlib import Path
import pandas as pd
import numpy as np
from nbformat import read, NO_CONVERT
import re
import glob
from github import Github
import git


def gettoken():
    """Get the token as an input from the user

    Returns:
        str : A token created on the https://github.ubc.ca

    Example:
    gettoken()
    """
    token = input(
        "Enter a valid token generated from github.ubc.ca to get the details from remote: "
    )
    return token


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
        # Navigate to the root of labzen repo to test the package using
        # dummy files (dummylab.ipynb and dummylab.Rmd).
        parse_lab("data-raw/dummylab.ipynb")
        parse_lab("data-raw/dummylab.Rmd")

        # Alternatively, navigate to a student assignment repo and run the
        # following code.
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
        # Navigate to the root of labzen repo and run the following code
        # using the dummy files:

        # for jupyter notebook:
        df, tab = count_points("data-raw/dummylab.ipynb")
        print(df)
        print(tab)

        # for Rmarkdown:
        df, tab = count_points("data-raw/dummylab.Rmd")
        print(df)
        print(tab)

        # Alternatively, navigate to a student assignment repo and run the
        # following code.
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


def check_repo_link(file_name: str = None):
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
        # Navigate to the root of labzen repo and run the following code
        # using the dummy files:

        # for jupyter notebook:
        check_repo_link("data-raw/dummylab.ipynb")

        # for Rmarkdown:
        check_repo_link("data-raw/dummylab.Rmd")

        # Alternatively, navigate to a student assignment repo and run the
        # following code.
        check_repo_link()
    """

    # Parse a lab file into its markdown blocks
    res = parse_lab(file_name)

    df = pd.DataFrame({"block": np.arange(1, len(res) + 1), "txt": res})

    # finding out if there is any link
    rex = (
        r"((https://)?(www.)?github\.ubc\.ca\/MDS-\d{4}-\d{2}\/DSCI_\d{3}_lab\d_[a-z]+)"
    )
    df["link"] = df["txt"].str.contains(rex, regex=True)

    # displaying the result in boolean
    repo_link = df["link"].any()
    if repo_link:
        print("Check 3: Repository link is included in the file")
        print(f"Check 3: {repo_link}")
    else:
        print("Check 3: Repository link is not included in the file")
        print(f"Check 3:", False)

    return repo_link


def check_lat_version(repo_name: str):
    """Check whether the user has pushed the latest version in his/her
        repository

    Args:
        repo_name (str): A repo name present under https://github.ubc.ca

    Returns:
        bool: a boolean output

    Example:
        # This function is still under development and difficult to test.
        # You will need a github token from github.ubc.ca.
        token = gettoken()
        check_lat_version("DSCI_599_lab1_jene3456")
    """
    # get the token from https://github.ubc.ca
    global token
    token = gettoken()
    g = Github(token, base_url="https://github.ubc.ca/api/v3")
    org = g.get_organization("MDS-2020-21")

    # get the repo name and and the last commit from the remote
    for repo in org.get_repos(type="all"):
        if repo.name == repo_name:
            print(repo.name)
            commit_remote = repo.get_commits()
            last_remotecommit = str(commit_remote[0])

            last_remotecommit = (
                last_remotecommit.replace("Commit(sha=", "")
                .replace('"', "")
                .replace(")", "")
            )
            print(last_remotecommit)

    # get the commit SHA from local repo
    val = input("Enter the local repo path for comparing the lastest version of repo: ")
    repo = git.Repo(val)

    commit_local = str(repo.head.commit)
    print(commit_local)

    # comparing the both SHAs
    if last_remotecommit == commit_local:
        print("Check 2: Remote has the latest version of the repository")
        print(f"Check 2: ", True)
    else:
        print("Check 2: Remote does not have the latest version of the repository")
        print(f"Check 2: ", False)
    return last_remotecommit == commit_local


def check_commits(repo_name: str):
    """Check whether the user has at least three commits

    Args:
        file_name (str): A repo name present under https://github.ubc.ca

    Returns:
        bool: a boolean output

    Example:
        # This function is still under development and difficult to test.
        # You will need a github token from github.ubc.ca.
        token = gettoken()
        check_commits("DSCI_599_lab1_jene3456")
    """
    # get the token from https://github.ubc.ca

    # token = gettoken()
    g = Github(token, base_url="https://github.ubc.ca/api/v3")
    org = g.get_organization("MDS-2020-21")

    # get the repo name and commits
    for repo in org.get_repos(type="all"):
        if repo.name == repo_name:
            print(repo.name)

            if repo.get_commits().totalCount >= 3:
                counter_invaliduser = 0
                counter_validuser = 0
                for commit in repo.get_commits():
                    # comapring the username with the commit author to get the commits only
                    # done by student's username
                    if g.get_user().name == commit.author.name:
                        counter_validuser = counter_validuser + 1
                        print(
                            commit,
                            commit.commit.committer,
                            commit.commit.author.email,
                            commit.commit.author.date,
                            commit.author.name,
                        )

                    else:
                        counter_invaliduser = counter_invaliduser + 1

                if counter_validuser >= 3:

                    print(
                        f"Check 1: Repository has at least 3 commits with the student username"
                    )
                    print(f"Check 1: ", True)

                    break

                if counter_invaliduser >= 3:

                    print(
                        f"Check 1: Repository does not have 3 commits with the student username"
                    )
                    print(f"Check 1: ", False)

            else:
                print(f"Check 1: Repository:{repo.name} has less than 3 commits")
                print(f"Check 1: ", False)
    return counter_validuser >= 3


def check_mechanics(repo_name: str, file_name: str = None):
    """Performs Mechanics Checks on a MDS Lab
       This function check that you have a Github repo link, that you have
       pushed your latest commit, and that you have at least three commit
       messages authored by you in your history.

    Args:
        repo_name (str) : A repo name present under https://github.ubc.ca.
            For the moment this variable should be provided by the user.

        file_name (str): A path or list of paths to MDS lab files (either
            .ipynb or .Rmd). If left blank, the function will recursively
            search for all labs in the working directory based on the file
            extension.

    Returns:
        bool : A boolean whether all checks passed. The function also prints
            informative messages as side texts.

    Example:
        check_mechanics("DSCI_599_lab1_jene3456", "/labzen/data-raw/dummylab.ipynb")
    """

    result = [
        check_commits(repo_name),
        check_lat_version(repo_name),
        check_repo_link(file_name),
    ]

    return all(result)
