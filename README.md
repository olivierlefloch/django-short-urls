PyWork4Core
===========

Core Work4 for Python applications

Use as a git subtree
====================

Add pywork4core as a subtree (assuming you have a copy of PyWork4Core in `../`):

    ../pywork4core/bin/git/install_subtree.sh

Get changes from pywork4core into new-project:

    make git_subtree_pull

Send changes to pywork4core from new-project:

    make git_subtree_push

See also <https://work4labs.atlassian.net/wiki/display/SYS/Integrating+PyWork4Core+into+a+new+project>

Typical usage
=============

  - Installation

        make install

  - Lint and tests

        make lint_and_test_report

Install PhantomJS dependency
============================

Just write the following line in your project's Makefile:

    USE_PHANTOMJS = TRUE

Then, the phantomjs binary would be installed at pywork4core/bin/phantomjs. You can also specify the
the version you want installed using PHANTOM_VERSION variable.
