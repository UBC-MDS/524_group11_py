from labzen import __version__
from labzen import labzen as lz
from pathlib import Path
import pytest


def test_version():
    assert __version__ == "0.1.0"


def test_parse_lab():
    # Define to test files
    pyfile = Path("data-raw/dummylab.ipynb")
    rfile = Path("data-raw/dummylab.Rmd")

    assert type(lz.parse_lab("data-raw/dummylab.ipynb")[0]) == type(
        "# DSCI 563 - Unsupervised Learning"
    )
    assert lz.parse_lab("data-raw/dummylab.ipynb")[4] == '## Imports <a name="im"></a>'
    assert len(lz.parse_lab("data-raw/dummylab.ipynb")) == 24
    with pytest.raises(Exception):
        lz.parse_lab("lab1.csv")
    with pytest.raises(Exception):
        lz.parse_lab(4)


def test_count_points():
    # Define to test files

    pyfile = "data-raw/dummylab.ipynb"
    rfile = "data-raw/dummylab.Rmd"

    # Test that the return types are dataframes
    df, tab = lz.count_points(pyfile, margins=False)
    assert type(tab).__name__ == "DataFrame"
    assert type(df).__name__ == "DataFrame"

    # Test that the objects are the right dimension (ipynb)
    df, tab = lz.count_points(pyfile, margins=False)
    assert tab.shape == (2, 3)
    df, tab = lz.count_points(pyfile, margins=True)
    assert tab.shape == (3, 3)

    # Test that the objects are the right dimension (Rmd)
    df, tab = lz.count_points(rfile, margins=False)
    assert tab.shape == (2, 3)
    df, tab = lz.count_points(rfile, margins=True)
    assert tab.shape == (3, 3)