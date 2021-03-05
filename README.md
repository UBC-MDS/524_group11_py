# labzen 

![](https://github.com/UBC-MDS/labzen/workflows/build/badge.svg) [![codecov](https://codecov.io/gh/UBC-MDS/labzen/branch/main/graph/badge.svg)](https://codecov.io/gh/UBC-MDS/labzen) ![Release](https://github.com/UBC-MDS/labzen/workflows/Release/badge.svg) [![Documentation Status](https://readthedocs.org/projects/labzen/badge/?version=latest)](https://labzen.readthedocs.io/en/latest/?badge=latest)
[![Project Status: Concept – Minimal or no implementation has been done yet](https://www.repostatus.org/badges/latest/concept.svg)](https://www.repostatus.org/#concept)


`labzen` is a Python package that adds more [zen](https://en.wikipedia.org/wiki/Zen) to your student experience of working on [MDS](https://masterdatascience.ubc.ca/) labs. It lets you manage common tasks such as counting total marks in an assigment, and performs common checks for mechanics in your iPython notebooks and R markdown assignments.

## Installation

```bash
$ pip install -i https://test.pypi.org/simple/ labzen
```

## Features

**labzen** helps members of the [UBC Master of Data Science (MDS)](https://masterdatascience.ubc.ca/) manage lab assignments written in iPython notebooks and R markdown. The package saves precious student time by automating common tasks such as counting up total marks in a lab assignment, and performing common mechanical checks that can-- if overlooked-- lose a student easy marks.

The package is currently under development, but will include the following functions:

- **Function 1**: The internal `parse_lab()` function will take an MDS .ipynb or .Rmd lab and return its markdown contents as a list/vector of strings. The function will scrub out yaml, code blocks, and all other metadata.

- **Function 2**: `count_points()` will build upon the first function and further parse labs into sections using regex. Further string manipulation will determine how many optional and required points there are per section based on the rubric tags. The function will return a table of totals so that students can plan how many optionals they wish to complete.

- **Function 3**: `check_mechanics()` conduct and print a series of mechanics checks to screen. For example, the function will
    - Check that you have included a Github repo link;
	- Check that you have pushed the latest version; and
	- Check that you have at least three commits.

The package data will include a directory of public and/or dummy lab files (.ipynb and .Rmd). Private or unpublished lab files will not be committed to the repository.

To the authors' knowledge, no package yet exists in the Python ecosystem that serves this specific purpose. However, several existing packages will be used to power the functionality of `labzen`, including `GitPython`, `pandas`, and `nbformat`. Some other python repos and past assignments may be used as inspiration, such as the parsing work done in the _throughput database_ in DSCI 513.

A parallel implementation for R exists [here](https://github.com/UBC-MDS/labzenr).

## Dependencies

- TODO

## Usage

- TODO

## Documentation

The official documentation is hosted on Read the Docs: https://labzen.readthedocs.io/en/latest/

## Contributors

This package is authored by Sukhdeep Kaur, Kamal Moravej Jahromi, and Rafael Pilliard-Hellwig as part of an academic assignment in the UBC MDS program. For a full list of contributors, please see the [contributors tab](https://github.com/UBC-MDS/labzen/graphs/contributors). 

We warmly welcome and recognize contributions from the community at large. If you wish to participate, please review our [contributing guidelines](CONTRIBUTING.rst) and familiarize yourself with [Github Flow](https://blog.programster.org/git-workflows).
### Credits

This package was created with Cookiecutter and the UBC-MDS/cookiecutter-ubc-mds project template, modified from the [pyOpenSci/cookiecutter-pyopensci](https://github.com/pyOpenSci/cookiecutter-pyopensci) project template and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage).
