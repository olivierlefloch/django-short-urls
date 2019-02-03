# coding=utf-8

"""Urls for the django short urls application"""

from __future__ import unicode_literals

from django.conf.urls import url

from django_short_urls.static_view import StaticView
from django_short_urls import views


urlpatterns = [  # pylint: disable=invalid-name
    url(r'^robots\.txt$', StaticView.as_view(template_name='robots.txt', content_type='text/plain')),
    url(r'^humans\.txt$', StaticView.as_view(template_name='humans.txt', content_type='text/plain; charset=utf-8')),

    # A view that can be used to test exception handling
    url(r'^DivideByZeroPlease$', lambda request: 0 / 0),

    url(r'^api/v1/new$', views.new, name='new'),
    url(r'^(.*)$', views.main, name='main'),
]
