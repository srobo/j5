Submitting Changes
==================

This page details how to make and submit changes to the `j5` codebase.

Repositories
------------

The main repository for `j5` is available on GitHub_, and Pull Requests should be submitted there.

There is an additional repository available on GitLab_, although this is a mirror of the GitHub repo, and changes
should not be submitted there.

.. _GitHub: https://github.com/j5api/j5
.. _GitLab: https://gitlab.com/j5api/j5

Discussing Changes
------------------

In many cases, changes should be discussed on an issue prior to beginning work on them, particularly where the changes
make a breaking change to external APIs or are otherwise significant.

At the discussion stage, other contributors can give early feedback on the idea and suggest ways to implement it.

Publishing Changes
------------------

The first step to submit changes is to publish them so that other contributors can review and give feedback.

The mechanism to publish your changes depends on whether you have write access to the repository. Write access
is granted by the Steering Council to recurrent, or trusted contributors.

* Contributors with write access should publish a branch on the repository.
* Contributors without write access should publish as a branch on a fork of the repository.

Pull Requests
-------------

The next stage is to submit a pull request (PR) to the GitHub repository. The PR will be used to give feedback on,
and discuss the changes with the contributor.

When making your PR, consider the following:

* Why do you want to make these changes?
* Which parts of the codebase do your changes affect?
* Have you updated the relevant documentation?
* Do your changes break the external API? Add the ``semver-major``, ``semver-minor`` or ``semver-patch`` label as appropriate.
* Do you want multiple reviewers to approve your code before merging?

If there is a related issue, make sure that your reference the issue number in your PR.

You may optionally request specific reviewers, and GitHub will often suggest people.

Review
------

Once changes have been submitted, it enters the review stage.

Guidelines for Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The first part of review is automated. CircleCI will automatically check your code. You can click on the green tick,
or red cross to see more information once the tests have been run. Your code cannot be merged until the automated tests
have passed.

You should receive feedback on your code from reviewers. You can then discuss the feedback, and make changes as needed.
When a reviewer is satisfied with your code, it will receive an approval and will be merged. You may find that several
cycles of review and changes are needed until your code is ready to be merged.


Guidelines for Reviewers
~~~~~~~~~~~~~~~~~~~~~~~~

When reviewing, ensure that you consider the following:

* Most importantly, give *positive* feedback. Our contributors dedicate their time and energy to submitting changes and
we need to ensure that we appreciated that.
* Check the results of the CI. Has it failed? Consider suggesting to the contributor why?
* Where possible, use the "Suggest Changes" feature on GitHub, this makes it easy to show what you are suggesting, and
allows the contributor to instantly apply your suggestions.
* In general, if you think many changes will be needed, focus on the major changes in the first round of review.
* Check any referenced issues to ensure that you have context for the changes.

Merge
-----

PRs can be merged once there is an approval. Code would usually be merged by the approving reviewer. However, there are
some circumstances where this may not be desired:

* Contributor has requested multiple review approvals
* Changes would be breaking and we cannot release a major version currently. This issue will be mitigated with LTS
branches, but we do not have any of these at this time.
