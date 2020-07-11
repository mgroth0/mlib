from http import HTTPStatus
import json
import unittest

import requests

from mlib.boot.mutil import query_url
from mlib.term import log_invokation
class SimpleAdminAPITest(unittest.TestCase):

    def __init__(self, simple_admin_api, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api = simple_admin_api

    @log_invokation()
    def _test_set(self, namespace, value, password=None):
        if value != self.api.GET_CODE:
            assert self.api.allow_set
        url = query_url(
            self.api.apiURL,
            {
                'message': json.dumps({
                    self.api.KEY_ARG_NAME         : namespace,
                    self.api.VALUE_OR_GET_ARG_NAME: value,
                    'password'                    : password
                })
            }
        )
        rr = requests.get(url)
        self.assertEqual(rr.status_code, HTTPStatus.OK)
        return rr.status_code, rr.text
    @log_invokation()
    def _test_get(self, namespace):
        assert self.api.allow_get
        return self._test_set(namespace, self.api.GET_CODE)


if __name__ == '__main__':
    unittest.main()
