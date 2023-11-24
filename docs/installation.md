# Installation

Currently, the only way to install "theme_boost_union_test_envs" is by acquiring it's source code and installing it directly.
There are no plans to change this, as this application was developed to aid the ongoing development of the "Boost Union" theme for Moodle.
There is no reason to have this application listed in a centralizedpackage installer like pip.

You will, however, need a working Python installation.
The [Python installation guide][] can guide you through the process.

## From source

The source for theme_boost_union_test_envs can be downloaded from
the [Github repo][].

You can either clone the public repository:

```shell
git clone git://github.com/eloquenza/theme_boost_union_test_envs
```

Or download the [tarball][] and extract it's sources:

```shell
curl -OJL https://github.com/eloquenza/theme_boost_union_test_envs/tarball/master
```

Next, make sure [poetry](https://python-poetry.org/docs/) and [conda](https://docs.conda.io/projects/miniconda/en/latest/) (either anaconda or miniconda is fine, or your preferred virtualenv tool) are installed.

Once you have a copy of the source, you should acquire the needed dependencies.
To not pollute your live system, you should create a virtual environment for python, and install the needed dependencies to run `boost-union-envs`:

```shell
conda create -n boost-union-envs python=3.11
conda activate boost-union-envs
poetry install
```

Afterwards, you can just run:

```shell
./boost-union-envs
```

This will present you with a help screen, which should - hopefully sufficiently enough - describe most commands.

The next time you want to run this application, just make sure to enter your virtualenv, if not already done so:

```shell
conda activate boost-union-envs
```


  [Python installation guide]: http://docs.python-guide.org/en/latest/starting/installation/
  [Github repo]: https://github.com/eloquenza/theme_boost_union_test_envs
  [tarball]: https://github.com/eloquenza/theme_boost_union_test_envs/tarball/master
