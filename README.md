# mdspyutils 

![](https://github.com/UBC-MDS/mdspyutils/workflows/build/badge.svg) [![codecov](https://codecov.io/gh/UBC-MDS/mdspyutils/branch/main/graph/badge.svg)](https://codecov.io/gh/UBC-MDS/mdspyutils) ![Release](https://github.com/UBC-MDS/mdspyutils/workflows/Release/badge.svg) [![Documentation Status](https://readthedocs.org/projects/mdspyutils/badge/?version=latest)](https://mdspyutils.readthedocs.io/en/latest/?badge=latest)
[![Project Status: Concept – Minimal or no implementation has been done yet](https://www.repostatus.org/badges/latest/concept.svg)](https://www.repostatus.org/#concept)


A Python package to help MDS students manage their labs in iPython notebooks and R markdown.

## Installation

```bash
$ pip install -i https://test.pypi.org/simple/ mdspyutils
```

## Features

**mdspyutils** helps members of the [UBC Master of Data Science (MDS)](https://masterdatascience.ubc.ca/) manage lab assignments written in iPython notebooks and R markdown. The package saves precious student time by automating common tasks such as counting up total marks in a lab assignment, and performing common mechanical checks that can-- if overlooked-- lose a student easy marks.

The package is currently under development, but will include the following functions:

- **Function 1**: The internal `parse_lab()` function will take an MDS .ipynb or .Rmd lab and return its markdown contents as a list/vector of strings. The function will scrub out yaml, code blocks, and all other metadata.

- **Function 2**: `count_points()` will build upon the first function and further parse labs into sections using regex. Further string manipulation will determine how many optional and required points there are per section based on the rubric tags. The function will return a table of totals so that students can plan how many optionals they wish to complete.

- **Function 3**: `check_mechanics()` conduct and print a series of mechanics checks to screen. For example, the function will
    - Check that you have included a Github repo link;
	- Check that you have pushed the latest version; and
	- Check that you have at least three commits.

The package data will include a directory of public and/or dummy lab files (.ipynb and .Rmd). Private or unpublished lab files will not be committed to the repository.

To the authors' knowledge, no package yet exists in the Python ecosystem that serves this specific purpose. However, several existing packages will be used to power the functionality of `mdspyutils`, including `GitPython`, `pandas`, and `nbformat`. Some other python repos and past assignments may be used as inspiration, such as the parsing work done in the _throughput database_ in DSCI 513.

## Dependencies

- TODO

## Usage

- TODO

## Documentation

The official documentation is hosted on Read the Docs: https://mdspyutils.readthedocs.io/en/latest/

## Contributors

We welcome and recognize all contributions. You can see a list of current contributors in the [contributors tab](https://github.com/UBC-MDS/mdspyutils/graphs/contributors).

### Credits

This package was created with Cookiecutter and the UBC-MDS/cookiecutter-ubc-mds project template, modified from the [pyOpenSci/cookiecutter-pyopensci](https://github.com/pyOpenSci/cookiecutter-pyopensci) project template and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage).
