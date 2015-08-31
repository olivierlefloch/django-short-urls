# coding=utf-8

from __future__ import unicode_literals

import socket
import subprocess

from django_app.no_network_test_case import NoNetworkTestCase, NetworkError
import requests


class NoNetworkTestCaseTestCase(NoNetworkTestCase):
    def test_socket(self):
        self.assertRaises(NetworkError, socket.socket)

    def test_requests(self):
        with self.assertRaises(NetworkError):
            # With kwargs to test that NoNetworkTestCase.guard accepts them
            requests.get("http://www.work4labs.com", auth=("user", "pass"))

    def test_networking_setup(self):
        # Ensures that setUp methods are also prevented from performing network requests
        self.assertEqual(subprocess.check_output(['python', __file__]), "")


if __name__ == "__main__":  # pragma: no cover
    class InternalTestCase(NoNetworkTestCase):  # pylint: disable=too-many-public-methods
        """
        This is tested via no_network_test_case_test
        Ensures that setUp methods are also prevented from performing network
        requests.
        """
        def setUp(self):
            socket.socket()

        def runTest(self):  # pylint: disable=invalid-name
            """Nothing to do, we're testing the setUp ;)"""
            pass

    try:
        InternalTestCase.setUpClass()
        InternalTestCase().setUp()
    except NetworkError:
        pass
    else:
        assert False, "InternalTestCase did not raise a NetworkError in setUp"
