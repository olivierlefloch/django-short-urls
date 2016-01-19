# django-short-urls

[![Circle CI](https://circleci.com/gh/Work4Labs/django-short-urls/tree/master.png?style=shield&circle-token=5d7460a8d2e37a2a2a7d410470d12109cccd93d3)](https://circleci.com/gh/Work4Labs/django-short-urls/tree/master)
[![Dependency Status](https://www.versioneye.com/user/projects/569e703b2025a6003a00034c/badge.svg)](https://www.versioneye.com/user/projects/569e703b2025a6003a00034c)

For dependencies see `requirements.txt`.

## Installation

Add a `local_settings.py` file in directory `django_short_urls` with

    cp local_settings.tpl.py local_settings.py
    vi local_settings.py

Setup your web server to load the `wsgi.py` file.

Add a new user to your database using the Django shell:

    % ./manage.py shell                                                                                         ~/Dropbox/Work4Labs/django-short-urls
    >>> from django_short_urls.models import User
    >>> User(login='work4labs', api_key='mysecretkey', email="root@work4labs.com").save()
    <User: User object>

You can then register new urls via requests to the API such as (take care to
url encode urls):

    % curl -d "prefix=work4labs&short_path=corporate&long_url=http://www.work4labs.com/" "http://work4labs:mysecretkey@workfor.us/api/v1/new"
    work4labs/corporate -> http://www.work4labs.com/

Once that is done `http://workfor.us/work4labs/corporate` will redirect to
`http://www.work4labs.com/`.

Work4 Labs internal documentation at
https://work4labs.atlassian.net/wiki/pages/viewpage.action?pageId=24248366
