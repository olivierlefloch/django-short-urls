# coding=utf-8

from __future__ import unicode_literals

from django_app import default_settings, models
from django_app.test import PyW4CTestCase


class DjangoAppTest(PyW4CTestCase):
    def test_default_settings(self):
        # pylint: disable=invalid-name
        APP_NAME = 'django_app'
        DEBUG = True

        settings_dict = dict(default_settings.init_settings(app_name=APP_NAME, debug=DEBUG))

        self.assertEqual(settings_dict['TEMPLATE_DEBUG'], DEBUG)
        self.assertEqual(settings_dict['TIME_ZONE'], None)
        self.assertIn(APP_NAME, settings_dict['APP_ROOT_DIR'])

    def test_env_to_bool(self):
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

    def test__compute_middleware_settings(self):
        common = 'django.middleware.common.CommonMiddleware'

        self.assertEqual(default_settings._compute_middleware_settings(), (common,))

        self.assertEqual(
            default_settings._compute_middleware_settings(early=('a',), late=('c',)),
            ('a', common, 'c'))

        self.assertEqual(
            default_settings._compute_middleware_settings(early=('a',), late=('c',), use_sentry=True),
            (
                'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',
                'raven.contrib.django.raven_compat.middleware.Sentry404CatchMiddleware',
                'a', common, 'c'
            )
        )

    def test_models(self):
        # Check that we can import the models file
        self.assertIn('Work4', models.__doc__)
