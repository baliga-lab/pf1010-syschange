#!/usr/bin/env python3

"""png_util_test.py
"""
import unittest
import xmlrunner
import sys
import json
from app import app

class APITest(unittest.TestCase):  # pylint: disable-msg=R0904

    """Test class for png_util"""
    def setUp(self):
        self.app = app.test_client()

    def test_api_info(self):
        """test the summary() function"""
        info = json.loads(self.app.get('/api/v1.0.0/info').data.decode('utf-8'))
        self.assertEquals(info['name'], "pf1010-syschange")
        self.assertEquals(info['version'], "1.0.0")


if __name__ == '__main__':
    SUITE = []
    SUITE.append(unittest.TestLoader().loadTestsFromTestCase(APITest))
    if len(sys.argv) > 1 and sys.argv[1] == 'xml':
      xmlrunner.XMLTestRunner(output='test-reports').run(unittest.TestSuite(SUITE))
    else:
      unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(SUITE))
