django-short-urls
=================

Dependencies:

  - mongoengine

Installation:

Add a `local_settings.py` file in directory `django_short_urls`, its content should look like:

    DEBUG = False
    
    ADMINS = (
        ('Work4 Labs Root', 'root@work4labs.com'),
    )
    
    MONGOENGINE = {
        'db': 'work4labs',
        'host': 'localhost',
        'port': 27017,
        'username': 'work4labs',
        'password': 'work4labs'
    }
    
    # Make this unique, and don't share it with anybody.
    SECRET_KEY = '6r__q4gindk5hzbb^)u!q%4-!d&amp;clxu#%0g3v4m@rg7!xf$#=@'

Setup your web server to load the `wsgi.py` file.

Add a new user to your database using the Django shell:

    % ./manage.py shell                                                                                         ~/Dropbox/Work4Labs/django-short-urls
    >>> from django_short_urls.models import User
    >>> User(login='work4labs', api_key='work4labs', email="root@work4labs.com").save()
    <User: User object>

You can then register new urls via requests to the API such as (take care to url encode urls):

    % curl -d "login=work4labs&api_key=work4labs&short_path=work4labs/corporate&long_url=http://www.work4labs.com/" "http://workfor.us/api/v1/new"
    work4labs/corporate -> http://www.work4labs.com/

Once that is done `http://workfor.us/work4labs/corporate` will redirect to `http://www.work4labs.com/`.
