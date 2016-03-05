# coding=utf-8

"""Urls for the django short urls application"""

from __future__ import unicode_literals

from django.conf.urls import patterns, url

from django_short_urls.static_view import StaticView


urlpatterns = patterns(  # pylint: disable=invalid-name
    '',
    (r'^robots\.txt$', StaticView.as_view(template_name='robots.txt', content_type='text/plain')),
    (r'^humans\.txt$', StaticView.as_view(template_name='humans.txt', content_type='text/plain; charset=utf-8')),

    # A view that can be used to test exception handling
    (r'^DivideByZeroPlease$', lambda request: 0 / 0),

    url(r'^api/v1/new$', 'django_short_urls.views.new', name='new'),
    url(r'^(.*)$', 'django_short_urls.views.main', name='main'),
)
