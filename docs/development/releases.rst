Releases
========

This page contains information on how we make releases of `j5` and what the process for releasing is.

Milestones
----------

Every version that will be released, with the exception of hotfix releases, will be added as a milestone on GitHub, such
that one can see at a glance what work needs to be done before those features are released. All issues with the
exception of patches are likely to be added to a milestone so that we know when it will be released to end users.

Locations
---------

We release `j5` to two major locations:

- PyPI_
- GitHub_

The most important of these two locations is PyPI_, as this will allow users to specify `j5` as a dependency for their
API and `pip` will be able to resolve and download our package, and our dependencies also.

The release should also be created as a 'release' on GitHub, with a git tag, version number and description of the
changes that have been made since the previous release. Any binary files associated with the release, such as wheels,
should also be uploaded to GitHub at this point. It should be ensured that these binaries match those that are uploaded
to PyPI.

.. _PyPI: https://pypi.org/project/j5/
.. _GitHub: https://github.com/j5api/j5

Version Strategy
----------------

As a general rule, `j5` will follow `Semantic Versioning`_.

Early Development
~~~~~~~~~~~~~~~~~

During early development of `j5`, we will be using version numbers of the format `0.y.z`, where `y` increments when new
features are added and `z` increments when a patch version is released. During this phase of development, the API is
considered to be unstable and subject to change.

Mature Development
~~~~~~~~~~~~~~~~~~

After early development is finished, `j5` will use a combination of `Semantic Versioning`_ and ideas taken from
`Git Flow`_. In particular, the concept of release branches for major versions and having multiple major and minor
versions in maintenance at any one time. Those who are running a competition should never ship an increment to the major
version number during a competition cycle as this will break the code of their teams. All versions where the major
version number is greater than `0` should be considered to be stable and will undergo additional testing before release.

.. _`Semantic Versioning`: https://semver.org/
.. _`Git Flow`: https://datasift.github.io/gitflow/IntroducingGitFlow.html

Release Process
---------------

* Make a commit that bumps the version numbers in `j5/__init__.py` and `pyproject.toml` to the new version, and merge it
  to master.
* Ensure you have this commit checked out, then run `poetry publish --build` and follow the instructions. This publishes
  the release to PyPI.
* Go to https://github.com/j5api/j5/releases/new.
* Tag version should be of the form "v0.7.3".
* Title should be of the form "Release 0.7.3".
* Enter a release description outlining the changes made since the previous release. `git log v0.7.2..master` might be
  useful here.
* Upload the artifacts that were built by `poetry publish --build` earlier. They can be found in the `dist` subdirectory.
* Click publish!
