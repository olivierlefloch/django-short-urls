# coding=utf-8

from __future__ import unicode_literals

from unittest import TestCase

from django_app import default_settings, models


class DjangoAppTest(TestCase):
    def test_default_settings(self):
        # pylint: disable=C0103
        APP_NAME = 'django_app'
        DEBUG = True

        settings_dict = dict(default_settings.init_settings(APP_NAME=APP_NAME, DEBUG=DEBUG))

        self.assertEqual(settings_dict['TEMPLATE_DEBUG'], DEBUG)
        self.assertEqual(settings_dict['TIME_ZONE'], None)
        self.assertIn(APP_NAME, settings_dict['APP_ROOT_DIR'])

    def test_bool(self):
        self.assertFalse(default_settings.env_to_bool('False'))
        self.assertFalse(default_settings.env_to_bool(0))
        self.assertFalse(default_settings.env_to_bool(''))
        self.assertFalse(default_settings.env_to_bool('FALSE'))
        self.assertFalse(default_settings.env_to_bool('NO'))
        self.assertFalse(default_settings.env_to_bool('JLHSDGLHQSG'))

        self.assertTrue(default_settings.env_to_bool('1'))
        self.assertTrue(default_settings.env_to_bool(1))
        self.assertTrue(default_settings.env_to_bool(42))
        self.assertTrue(default_settings.env_to_bool(-1))
        self.assertTrue(default_settings.env_to_bool('true'))
        self.assertTrue(default_settings.env_to_bool('YES'))

    def test_models(self):
        # Check that we can import the models file
        self.assertIn('Work4', models.__doc__)
