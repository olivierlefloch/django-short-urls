# coding=utf-8

"""
This module contains utility methods for mongo.
"""

from __future__ import unicode_literals

import re

import mongoengine


def mongoengine_is_primary():
    """Checks if the current mongoengine connection is to a primary"""
    return mongoengine.connection.get_connection().is_primary


class LocalURLField(mongoengine.URLField):
    """
    A URLField extension that allows local urls. For that we allow URLs of the form
        /\\S*
    meaning any non-whitespace string (of any length, even empty) that starts with a `/`, or
    a regular URL (leveraging the existing mongoengine.URLField._URL_REGEX.pattern).
    """
    _URL_REGEX = re.compile(
        r'^/\S*$|' + mongoengine.URLField._URL_REGEX.pattern,  # pylint: disable=protected-access
        re.IGNORECASE)

    def validate(self, value):
        """
        Need to customize this validator to avoid checking the scheme.
        This replicates a lot of code from the parent validator and works around it's
        limitations (can't avoid checking the scheme), so we don't call `super` here.
        """
        # Check first if the scheme is valid
        scheme = value.split('://')[0].lower()
        if '://' in value and scheme not in self.schemes:
            self.error('Invalid scheme {} in URL: {}'.format(scheme, value))
        elif not self.url_regex.match(value):
            self.error('Invalid URL: {}'.format(value))


def get_document_or_404(klass, *filter_args, **filter_kwargs):
    """Retrieve Document for given pk value or return a 404 HTTP response"""
    try:
        return klass.objects.get(*filter_args, **filter_kwargs)  # pylint: disable=no-member
    except klass.DoesNotExist:  # pylint: disable=no-member
        from django.http import Http404
        raise Http404('No match found.')
