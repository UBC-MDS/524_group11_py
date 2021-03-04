from labzen import __version__
from labzen import labzen as lz
from pathlib import Path

def test_version():
    assert __version__ == "0.1.0"


def test_count_points():
    # Define to test files
    pyfile = Path("data-raw/dummylab.ipynb")
    rfile = Path("data-raw/dummylab.Rmd")

    # Test that the return types are dataframes
    df, tab = lz.count_points(pyfile, margins=False)
    assert type(tab).__name__ == "DataFrame"
    assert type(df).__name__ == "DataFrame"

    # Test that the objects are the right dimension (ipynb)
    df, tab = lz.count_points(pyfile, margins=False)
    assert tab.shape == (2, 2)
    df, tab = lz.count_points(pyfile, margins=True)
    assert tab.shape == (3, 2)

    # Test that the objects are the right dimension (Rmd)
    df, tab = lz.count_points(rfile, margins=False)
    assert tab.shape == (2, 2)
    df, tab = lz.count_points(rfile, margins=True)
    assert tab.shape == (3, 2)