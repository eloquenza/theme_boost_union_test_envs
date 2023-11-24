# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

Please try to use the [Google style guide](https://google.github.io/styleguide/pyguide.html) whereever possible.
This way we all have more time arguing about semantics and the project's future instead of pedantic issues.

You can contribute in many ways:

## Types of Contributions

### Report Bugs

Report bugs as a [GitHub issue](https://github.com/eloquenza/theme_boost_union_test_envs/issues).

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" is open to whoever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "feature::nice-to-have" is open to whoever wants to implement it.
Other issues with other tags might need communication and coordination with a maintainer.

### Write Documentation

`theme_boost_union_test_envs` could always use more documentation, whether as part of the
official `theme_boost_union_test_envs` docs, in docstrings or via helpful posts, snippets or workflows for your colleagues.

### Submit Feedback

The best way to send feedback is to file an issue at https://github.com/eloquenza/theme_boost_union_test_envs/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

## Get Started!

Ready to contribute? Here's how to set up `theme_boost_union_test_envs` for local development.

1. Fork the `theme_boost_union_test_envs` repo on GitHub.
2. Clone your fork locally

```shell
    git clone git@github.com:your_name_here/theme_boost_union_test_envs.git
```

1. Ensure [poetry](https://python-poetry.org/docs/) and [conda](https://docs.conda.io/projects/miniconda/en/latest/) (either anaconda or miniconda is fine, or your preferred virtualenv tool) are installed.
2. Start your virtualenv and install dependencies:

```shell
    conda create -n boost-union-envs python=3.11
    conda activate boost-union-envs
    poetry install
```

5. Create a branch for local development:

```shell
    git checkout -b name-of-your-bugfix-or-feature
```

   Now you can make your changes locally.

6. When you're done making changes, check that your changes pass the
   tests, including testing other Python versions, with tox:

```shell
    tox
```

7. Commit your changes and push your branch to GitHub:

```shell
    git add .
    git commit -m "Your detailed description of your changes."
    git push origin name-of-your-bugfix-or-feature
```

8. Submit a pull request through the GitHub website.

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.md.
3. The pull request should work for Python atleast for 3.11. Check
   https://github.com/eloquenza/theme_boost_union_test_envs/actions
   and make sure that the tests pass for all supported Python versions.

## Tips

To run a subset of tests.

```shell
pytest tests.test_theme_boost_union_test_envs
```

## Deploying

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed (including an entry in HISTORY.md).
Then run:

```shell
poetry patch # possible: major / minor / patch
git push
git push --tags
```
