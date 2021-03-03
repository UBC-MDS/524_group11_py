from labzen import __version__
from labzen import labzen as lz
from pathlib import Path

def test_version():
    assert __version__ == "0.1.0"


def test_count_points_type():
    # Test that the return type is a dataframe
    labfile = Path("data-raw/dummylab.ipynb")
    tab = lz.count_points(labfile, margins=False)
    assert type(tab) == "pandas.core.frame.DataFrame"


def test_ipynb_points_2_rows():
    labfile = Path("data-raw/dummylab.ipynb")
    tab = lz.count_points(labfile, margins=False)
    assert tab.shape == (2, 2)


def test_ipynb_points_2_rows():
    labfile = Path("data-raw/dummylab.ipynb")
    tab = lz.count_points(labfile, margins=True)
    assert tab.shape == (3, 2)


def test_rmd_points_2_rows():
    labfile = Path("data-raw/dummylab.rmd")
    tab = lz.count_points(labfile, margins=False)
    assert tab.shape == (2, 2)


def test_rmd_points_2_rows():
    labfile = Path("data-raw/dummylab.rmd")
    tab = lz.count_points(labfile, margins=True)
    assert tab.shape == (3, 2)