from labzen import labzen as lz
import pytest
import mock


def test_parse_lab():

    # Test for user input
    with mock.patch("builtins.input", return_value=1):
        assert type(lz.parse_lab()).__name__ == "list"

    # Define to test files
    pyfile = "data-raw/dummylab.ipynb"
    rfile = "data-raw/dummylab.Rmd"

    parsed_lab_py = lz.parse_lab(pyfile)
    parsed_lab_r = lz.parse_lab(rfile)

    # Test that the return type is list
    assert type(parsed_lab_py).__name__ == "list"
    assert type(parsed_lab_r).__name__ == "list"

    # Test that the elements of list is string
    assert type(parsed_lab_py[0]).__name__ == "str"
    assert type(parsed_lab_r[0]).__name__ == "str"

    # Test if the right cell type parsed
    assert parsed_lab_py[4] == '## Imports <a name="im"></a>'
    assert len(parsed_lab_r[2]) == 760

    # Test if all markdown cells has been parsed
    assert len(parsed_lab_py) == 24
    assert len(parsed_lab_r) == 4

    # Test if the function raise exception for a wrong input
    with pytest.raises(Exception):
        lz.parse_lab("lab1.csv")
    with pytest.raises(Exception):
        lz.parse_lab(99)


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


def test_check_repo_link():
    # Define to test files
    pyfile = "data-raw/dummylab.ipynb"
    rfile = "data-raw/dummylab.Rmd"

    # run the check for dummy files
    py_link = lz._check_repo_link(pyfile)
    r_link = lz._check_repo_link(rfile)

    # Test that the return type is boolen
    assert type(py_link).__name__ == "bool_"
    assert type(r_link).__name__ == "bool_"

    # .ipynb has no link and should return false
    assert not py_link
    # .rmd has a link and should return true
    assert r_link

    # Test if the function raise exception for a wrong input
    with pytest.raises(Exception):
        lz._check_repo_link(4)
    with pytest.raises(Exception):
        lz._check_repo_link("a_file_that_does_not_exist.ipynb")
