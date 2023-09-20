# Test environments for the Moodle theme "Boost Union"

Explicit IaC environments based on containers.
Allows for the creation of several containers containing Moodle in different versions.

* Documentation: <https://eloquenza.github.io/theme_boost_union_test_envs/>

## Requirements

* Docker
* Git
* Python

## Motivation for this project

"Moodle an Hochschulen e.V." identified the requirement for a centralized test server to ease the development of the "Boost Union" theme, esp. with ever increasing workloads, needs of the various stakeholders and the new Moodle UI changing ever so slightly with each version.

## Features

* TODO

## Installation

For development, use a virtualenv as per usual of Python.
You are not restricted to use a specific venv tool, but I recommend anaconda / miniconda.

Start your virtualenv:

```bash
conda create -n boost-union-envs python=3.11
```

Start and leave your virtual environment like this:

```bash
conda activate boost-union-envs
conda deactivate
```

To ensure reproducible builds and a homogenous development environment, we use poetry as a dependency manager.
If you wish to test this application or help during it's development, start your virtualenv and enter the following command:

```bash
poetry install
```

Poetry automatically installs all dependencies needed to run this project.

In case the pre-commit hooks are not working, please re-add them on your own via:

```bash
pre-commit install
```

## Usage

## Settings

## Maintainers

## Contributors

## Copyright

* Free software: GPL-3.0-only

## Credits

The base of this application was created with the [ppw](https://zillionare.github.io/python-project-wizard) tool. For more information, please visit the [project page](https://zillionare.github.io/python-project-wizard/).
The project template was adapted a bit because the project's author was more accustomed to a streamlined pyproject.toml.
