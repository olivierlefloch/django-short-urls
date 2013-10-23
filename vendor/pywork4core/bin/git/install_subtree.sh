#!/usr/bin/env bash

git remote add pywork4core git@github.com:Work4Labs/pywork4core.git
git subtree add -P vendor/pywork4core --squash -m"Install PyWork4Core as a git subtree" pywork4core master
