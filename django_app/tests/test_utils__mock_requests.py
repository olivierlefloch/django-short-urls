# coding=utf-8

from __future__ import unicode_literals

import requests
from requests.exceptions import HTTPError

from django_app.test import PyW4CTestCase
from utils.mock_requests import patch_requests, patch_requests_decorator


class UtilsMockRequestsTest(PyW4CTestCase):
    requests_mock_dec_test_url = "http://testing.work4labs.com"

    def test_base_case(self):
        # Check that the mock behaves when used properly
        test_url = "http://test.work4labs.com"
        fail_test_url = "http://kaboom.work4labs.com"
        mapping = {
            test_url: {
                'response': 'Nothingness',
                'http_code': 200
            },
            fail_test_url: {
                'response': 'Nope',
                'http_code': 500
            }
        }

        with patch_requests(mapping) as m_requests:
            # All good, take 1
            resp = requests.post(test_url)
            self.assertEqual(m_requests['post'].call_count, 1)
            self.assertEqual(m_requests['post'].call_args[0][0], test_url)
            self.assertEqual(resp.url, test_url)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Nothingness', resp.text)

            # All good, take 2
            resp = requests.get(test_url)
            self.assertEqual(m_requests['get'].call_count, 1)
            self.assertEqual(m_requests['get'].call_args[0][0], test_url)
            self.assertEqual(resp.url, test_url)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Nothingness', resp.text)

            # Uh oh
            resp = requests.get(fail_test_url)
            self.assertEqual(m_requests['get'].call_count, 2)
            self.assertEqual(m_requests['get'].call_args[0][0], fail_test_url)
            self.assertEqual(resp.url, fail_test_url)
            self.assertEqual(resp.status_code, 500)
            self.assertIn('Nope', resp.text)
            with self.assertRaises(HTTPError):
                resp.raise_for_status()  # The mock behaves like a proper requests' Response

    @patch_requests_decorator({requests_mock_dec_test_url: {'response': 'Bah, humbug'}})
    def test_001_as_decorator(self):
        # Check that the mock behaves too when used properly as a decorator
        resp = requests.post(self.requests_mock_dec_test_url)
        self.assertEqual(resp.url, self.requests_mock_dec_test_url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Bah', resp.text)

    def test_002_empty_mapping(self):
        # An empty mapping does not crash − but using it will fail
        mapping = {}
        with patch_requests(mapping):
            with self.assertRaises(Exception):  # "called with unexpected URL…"
                requests.get("https://whatever.work4labs.com")

    def test_003_custom_headers_and_json(self):
        # B. Custom headers and json
        test_url = "https://whatever.work4labs.com"
        headers = {"x-api-key": 'Blablabla'}
        mapping = {
            test_url: {
                'headers': headers,
                'json': True,
                'response': ['Nothingness']
            }
        }
        with patch_requests(mapping) as m_requests:
            resp = requests.post(test_url)
            self.assertEqual(m_requests['post'].call_count, 1)
            self.assertEqual(m_requests['post'].call_args[0][0], test_url)
            self.assertEqual(resp.url, test_url)
            self.assertEqual(resp.headers, headers)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual('["Nothingness"]', resp.text)

    def test_004_request_method(self):
        # Using requests.request directly also work (kind of an edge case for coverage)
        test_url = "http://test.work4labs.com"
        mapping = {
            test_url: {
                'response': 'Nothingness',
                'http_code': 200
            }
        }
        with patch_requests(mapping) as m_requests:
            resp = requests.request('GET', test_url)
            self.assertEqual(m_requests['request'].call_count, 1)
            self.assertEqual(m_requests['request'].call_args[0][0], 'GET')
            self.assertEqual(m_requests['request'].call_args[0][1], test_url)
            self.assertEqual(resp.url, test_url)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Nothingness', resp.text)
