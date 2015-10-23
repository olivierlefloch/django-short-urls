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

        make lint test_and_report

Install PhantomJS dependency
============================

To install `PhantomJS` in your `venv`, override the `install_project` rule in your projects `Makefile` and have it
invoke the `install_phantomjs` rule:

    install_project:: install_phantomjs

The `phantomjs` binary will then be installed at `pywork4core/bin/phantomjs`. You can also specify the
the version you want installed with the `PHANTOM_VERSION` variable.
