# coding=utf-8

"""Static template view"""

from __future__ import unicode_literals

from django.http import HttpResponse
from django.template.loader import get_template
from django.views.generic.base import View


class StaticView(View):
    """A view that renders a static template."""
    template_name = None
    content_type = None

    def get(self, request):  # pylint: disable=unused-argument
        """Return an HttpResponse that retrieves its content from the template, with no additional formatting"""
        return HttpResponse(get_template(self.template_name).render(), self.content_type)
