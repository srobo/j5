Getting Started
===============

`j5` is developed on GitHub_ and pull requests should be submitted there. If you have write access to the repository,
you optionally can develop your changes on a branch within the main repository. Alternatively, please fork the `j5`
repository and pull request from there.

If you are working on something that has an existing issue open on the `j5` repository, please ensure that you assign
the issue to yourself such that duplication of work does not accidentally occur.

If you need help with Git, there are some good tutorial resources here:

- `Git - The Simple Guide`_
- `GitHub - Learning Git`_
- `Atlassian Git Tutorial`_

.. _`Git - The Simple Guide`: https://rogerdudler.github.io/git-guide/
.. _`GitHub - Learning Git`: https://try.github.io/
.. _`Atlassian Git Tutorial`: https://www.atlassian.com/git

Setting Up
----------

You will need the following installed on your machine:

- Python_ 3.7 or higher
- python3-pip (for package management)
- GNU Make
- poetry_

Now clone the repository from GitHub_ into a folder on your local machine.

Inside that folder, we need to tell `poetry` to install the dev dependencies: ``poetry install``

You can now enter the virtual environment using ``poetry shell`` and develop using your IDE of choice.

Testing
-------

As our code is used and viewed by students, we have a high standard of code within `j5`. All code must be statically
typed, linted and covered in unit tests.

You can run all of the required tests with one command: ``make``.

Unit Testing
~~~~~~~~~~~~

We use `pytest` and `coverage.py` to do our unit testing.

Execute the test suite: ``make test``

If you wish to view the `HTML` output from `coverage.py` to help you find statements that are not covered by unit tests,
you can run the test suite in `html-cov` mode.

Execute the test suite in `html-cov` mode: ``make test-cov``

Linting
~~~~~~~

We use `flake8` and a number of extensions to ensure that our code meets the `PEP 8` standards.

Execute the linter: ``make lint``

Static Type Checking
~~~~~~~~~~~~~~~~~~~~

We use `mypy` to statically type check our code.

Execute Type Checking: ``make type``

Documentation
-------------

We are using `Sphinx` to generate documentation for the project.

All documentation can be found in the ``docs/`` folder.

Generate HTML Documentation: ``make html``

.. _Quick Start: usage/quickstart
.. _GitHub: https://github.com/srobo/j5

.. _Python: https://www.python.org/
.. _poetry: https://poetry.eustace.io/

