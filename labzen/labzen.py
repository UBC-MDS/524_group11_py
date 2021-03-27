import os
from pathlib import Path
import pandas as pd
import numpy as np
from nbformat import read, NO_CONVERT
import re
import glob
from github import Github
import git
import warnings

import webbrowser


def _find_assignment(directory=None):
    """Find an Assignment Dyamically

    A helper function to validate and locate the a lab file based on its
    extension being Rmd ipynb. The utility will search recursively up the
    directory. If multiple candidate files are found, the user will be
    prompted to select which file they wish.

    Args:
        directory ([type], optional): A directory path to be searched
            recursively. If None given, will use the working directory.

    Returns:
        [str]: A path to the file selected.
    """
    if directory is None:
        directory = os.getcwd()

    types = ["*.ipynb", "*.Rmd"]
    files = []
    for type in types:
        pathname = directory + "/**/*" + type
        type_files = glob.glob(pathname, recursive=True)
        files += type_files
    names = [
        str(n + 1) + "." + os.path.basename(file)
        for n, file in enumerate(files)
    ]
    print("The existing files are:")
    for item in names:
        print(item)
    notebook = input("Enter your file number from the above list:")
    notebook = files[int(notebook) - 1]
    return notebook


def create_github_token(host="https://github.ubc.ca"):
    """Open A Browser to Generate a New Github Enterprise Token

    Args:
        host (str):
            The URL to the upstream host. Defaults to UBC Github Enterprise.
    Returns:
        None

    Examples:
        >>> from labzen import labzen as lz
        >>> # Open a web browser
        >>> lz.create_github_token()
    """
    opts = "scopes=repo,user,gist,workflow&description=LABZEN"
    url = f"{host}/settings/tokens/new?{opts}"
    webbrowser.open(url, new=2)


def parse_lab(notebook=None):
    """Parse MDS lab files to return the markdown content

    Args:
        notebook (str):
            A path or list of paths to MDS lab files (either .ipynb
            or .Rmd). If left blank, the function will recursively
            search for all labs in the working directory based on the file
            extension.

    Returns:
        list: Each element of list is a content of one markdown cell.

    Example:
        >>> # Download the demo files into the working directory
        >>> import urllib.request
        >>> from labzen import labzen as lz
        >>>
        >>> baseurl = (
        >>>     "https://raw.githubusercontent.com"
        >>>     + "/UBC-MDS/labzen/main/data-raw"
        >>> )
        >>> labs = {
        >>>     "dummylab.Rmd": f"{baseurl}/dummylab.Rmd",
        >>>     "dummylab.ipynb": f"{baseurl}/dummylab.ipynb",
        >>> }
        >>>
        >>> for name, url in labs.items():
        >>>     urllib.request.urlretrieve(url, name)
        >>>
        >>> # parse the labs
        >>> lz.parse_lab("dummylab.ipynb")
        >>> lz.parse_lab("dummylab.Rmd")
        >>>
        >>> # Alternatively, navigate to a student assignment repo and
        >>> # run the following code.
        >>> lz.parse_lab()
    """
    # If the user did not define the specific file, recursively
    # search for rmd and ipynb files in the working directory
    if notebook is None:
        notebook = _find_assignment()
    path = Path(notebook)
    _, extension = os.path.splitext(notebook)

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
        text_and_code = path.expanduser().read_text()
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
        >>> from labzen import labzen as lz
        >>> import urllib.request
        >>>
        >>> # Download the demo files into the working directory
        >>> baseurl = (
        >>>     "https://raw.githubusercontent.com"
        >>>     + "/UBC-MDS/labzen/main/data-raw"
        >>> )
        >>> labs = {
        >>>     "dummylab.Rmd": f"{baseurl}/dummylab.Rmd",
        >>>     "dummylab.ipynb": f"{baseurl}/dummylab.ipynb",
        >>> }
        >>> for name, url in labs.items():
        >>>     urllib.request.urlretrieve(url, name)
        >>>
        >>> # for Jupyter notebooks:
        >>> df, tab = lz.count_points("dummylab.ipynb")
        >>> print(df[["rubric", "points", "type"]])
                        rubric  points          type
        0            [mechanics]     [5]  Non-Optional
        1            [reasoning]     [4]  Non-Optional
        2  [accuracy, reasoning]  [3, 2]  Non-Optional
        3  [accuracy, reasoning]  [6, 4]      Optional
        4  [accuracy, reasoning]  [7, 3]      Optional
        5                  [viz]     [5]  Non-Optional
        >>> print(tab)
                   type  total  prop
        0  Non-Optional     19  0.95
        1      Optional     20  1.00
        2           All     39  1.95
        >>>
        >>> # for Rmarkdown:
        >>> df, tab = lz.count_points("dummylab.Rmd")
        >>> print(tab)
                type  total      prop
        0  Non-Optional     42  0.950000
        1      Optional     12  0.271429
        2           All     54  1.221429
        >>>
        >>> # Alternatively, navigate to a student assignment repo and run the
        >>> # following code.
        >>> df, tab = lz.count_points()
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


def _check_repo_link(file_name: str = None):
    """Check whether the user has included the github repo link in his/her
        repository

    Args:
        file_name (str):
            A path or list of paths to MDS lab files (either
            .ipynb or .Rmd). If left blank, the function will recursively
            search for all labs in the working directory based on the file
            extension.

    Returns:
        bool: a boolean output

    Example:
        >>> # Navigate to the root of labzen repo and run the following code
        >>> # using the dummy files:
        >>>
        >>> # for jupyter notebook:
        >>> _check_repo_link("data-raw/dummylab.ipynb")
        >>>
        >>> # for Rmarkdown:
        >>> _check_repo_link("data-raw/dummylab.Rmd")
        >>>
        >>> # Alternatively, navigate to a student assignment repo and run the
        >>> # following code.
        >>> _check_repo_link()
    """

    # Parse a lab file into its markdown blocks
    res = parse_lab(file_name)

    df = pd.DataFrame({"block": np.arange(1, len(res) + 1), "txt": res})

    # finding out if there is any link
    rex = re.compile(
        r"((https://)?(www.)?github\.ubc\.ca"  # base url for GH Enterprise
        r"\/MDS-\d{4}-\d{2}"  # organization
        r"\/DSCI_\d{3}_lab\d_[a-z]+)"  # lab repo with CWL username
    )
    warnings.filterwarnings("ignore", "This pattern has match groups")
    df["link"] = df["txt"].str.contains(rex, regex=True)

    # displaying the result in boolean
    repo_link = df["link"].any()
    if repo_link:
        print("Check 3: Repository link is included in the file")
        print(f"Check 3: {repo_link}")
    else:
        print("Check 3: Repository link is not included in the file")
        print("Check 3:", False)

    return repo_link


def _check_lat_version(path: str, token: str):
    """Check whether the user has pushed the latest version in his/her
        repository

    Args:
        path (str): A local file path to either a lab directory or to a
            lab file inside a local git directory.
        token (str): A token for https://github.ubc.ca

    Returns:
        bool: a boolean output

    Example:
        >>> from labzen import labzen as lz
        >>>
        >>> # navigate to a student repo and run:
        >>> token = "544c96ce0d3dc9b66ac8d70b32c07bd0c46129db"
        >>> lz._check_lat_version(token=token)
    """
    # locate the repo root
    local_repo = git.Repo(path, search_parent_directories=True)

    # locate the Github Enterprise repo name
    ghe = Github(token, base_url="https://github.ubc.ca/api/v3")
    ghe_repo = ghe.get_repo(__find_ghe_repo(local_repo))

    # find latest commit on GHE
    ghe_commit = ghe_repo.get_commits()[0].sha

    # find the latest local commit
    local_commit = str(local_repo.head.commit)

    # comparing the both SHAs
    if ghe_commit == local_commit:
        print("Check 2: Remote has the latest version of the repository")
        print("Check 2:", True)
    else:
        print(
            "Check 2: Remote does not have the latest version of the ",
            "repository",
        )
        print("Check 2:", False)
    return ghe_commit == local_commit


def __find_ghe_repo(local_repo, org="MDS-2020-21"):
    """Find a Github Repo Path

    Args:
        local_repo ([git.repo.base.Repo]): A local Github repository
        org (str): The name of the organization on Github Enterprise to search.
            Defaults to 'MDS-2020-21'.

    Returns:
        [type]: [github.Repository.Repository] An UBC GHE remote (student
            project repo).
    """
    # find the name of the repo on Github Enterprise
    remote_urls = [list(x.urls)[0] for x in local_repo.remotes]
    rex = "([A-Za-z0-9_-]+)(?=\\.git$)"
    ghe_name = list(set([re.search(rex, x).group(1) for x in remote_urls]))[0]

    return f"{org}/{ghe_name}"


def _check_commits(path: str, token: str, verbose=False):
    """Check whether the user has at least three commits

    Args:
        path (str): A local repo path or local file path to a lab.git
        token (str): A token for Github Enterprise.
        verbose (bool): Whether to print commit details to screen

    Returns:
        bool: a boolean output

    Example:
        >>> from labzen import labzen as lz
        >>>
        >>> path = "/Users/jene/MDS/Block5/lab/DSCI_599_lab1_jene3456"
        >>> token = "544c96ce0d3dc9b66ac8d70b32c07bd0c46129db"
        >>> lz._check_commits(path, token)
    """

    # locate the repo root
    local_repo = git.Repo(path, search_parent_directories=True)

    # locate the Github Enterprise repo name
    ghe = Github(token, base_url="https://github.ubc.ca/api/v3")

    try:
        # org/repo_name
        ghe_name = __find_ghe_repo(local_repo)
        ghe_repo = ghe.get_repo(ghe_name)
    except Exception:
        raise Exception(f"{ghe_name} not found on github.ubc.ca")

    # count the total number of commits on the remote
    ghe_commits = ghe_repo.get_commits()
    ghe_commit_n = ghe_commits.totalCount

    if ghe_commit_n > 3:
        student_name = ghe.get_user().name
        student_commits_n = 0
        for commit in ghe_commits:
            if student_name == commit.author.name:
                student_commits_n += 1

                if verbose:
                    print(
                        commit,
                        commit.commit.committer,
                        commit.commit.author.email,
                        commit.commit.author.date,
                        commit.author.name,
                    )
        check_result = student_commits_n > 3
    else:
        check_result = False

    # print check result to screen
    if check_result:
        print(
            "Check 1: Repository has at least 3 commits with the",
            f"student username {student_name}",
        )
        print("Check 1:", check_result)
    elif student_commits_n < 3:
        print(
            "Check 1: Repository does not have 3 commits with the"
            f"student username {student_name}"
        )
        print("Check 1:", check_result)
    else:
        print(
            f"Check 1: Repo {ghe_repo.name} has fewer than 3 commits",
            f"with the student username {student_name}",
        )
        print("Check 1:", check_result)

    return check_result


def check_mechanics(path: str = None, token=None):
    """Performs Mechanics Checks on a MDS Lab

       This function checks that you...
        1. ... have a Github repo link;
        2. ... have pushed your latest commit; and
        3. ... have at least three commit messages authored by you in
            your history.

    Args:
        path (str): A local path to a Github directory or an MDS lab file
            (.ipynb or .Rmd) within such a directory.

        token (str) : A personal access token for https://github.ubc.ca. See
            ``create_github_token()`` for details.

    Returns:
        bool : A boolean whether all checks passed. The function also prints
            informative messages as a side effect.

    Example:
        >>> from labzen import labzen as lz
        >>>
        >>> # Step 1: get a token
        >>> lz.create_github_token()
        >>>
        >>> # Step 2: check mechanics
        >>> file = "~/MDS/Block5/lab1/DSCI_599_lab1_jene3456"
        >>> token = "544c96ce0d3dc9b66ac8d70b32c07bd0c46129db"
        >>> lz.check_mechanics(file, token)
        Check 1: Repository has at least 3 commits with the student
        username JENE SMITH
        Check 1: True
        Check 2: Remote has the latest version of the repository
        Check 2: True
        Check 3: Repository link is included in the file
        Check 3: True
        >>>
        >>> # Alternatively, just run the following from an MDS lab directory:
        >>> lz.check_mechanics(token = token)

    """
    # use the current working directory if no path given
    if path is None:
        path = os.getcwd()

    # local the repo root
    repo_path = git.Repo(path, search_parent_directories=True).git_dir

    # local lab file
    _, extension = os.path.splitext(path)
    if extension == ".Rmd" or extension == ".ipynb":
        lab_path = path
    else:
        lab_path = _find_assignment(path)

    result = [
        _check_commits(repo_path, token=token),
        _check_lat_version(repo_path, token=token),
        _check_repo_link(lab_path),
    ]

    return all(result)
