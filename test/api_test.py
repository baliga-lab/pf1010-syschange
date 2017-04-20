#!/usr/bin/env python3

"""png_util_test.py
"""
import unittest
import xmlrunner
import sys
import json
from app import app

import mysql.connector


def dbconn():
    return mysql.connector.connect(host=app.config['DATABASE_HOST'],
                                   user=app.config['DATABASE_USER'],
                                   password=app.config['DATABASE_PASSWORD'],
                                   database=app.config['DATABASE_NAME'])

class APITest(unittest.TestCase):  # pylint: disable-msg=R0904

    """Test class for png_util"""
    def setUp(self):
        conn = dbconn()
        cursor = conn.cursor()
        try:
            cursor.execute('delete from system_changes')
            conn.commit()
        finally:
            cursor.close()
            conn.close()
        self.app = app.test_client()

    def test_api_info(self):
        """test the summary() function"""
        info = json.loads(self.app.get('/api/v1.0.0/info').data.decode('utf-8'))
        self.assertEquals(info['name'], "pf1010-syschange")
        self.assertEquals(info['version'], "1.0.0")

    def test_empty_syschanges(self):
        """test the initial sys changes status through the API function"""
        result = json.loads(self.app.get('/api/v1.0.0/system_changes/1/add_base').data.decode('utf-8'))
        self.assertEquals(result['change_type'], "add_base")
        self.assertEquals(len(result['changes']), 0)

    def test_put_syschange_invalid_date(self):
        """test the put sys change API function with an invalid date"""
        result = json.loads(self.app.put('/api/v1.0.0/system_change/1/add_base',
                                         data=json.dumps({
                                             'time': 'invalid date',
                                             'quantity': 12.3
                                         }),
                                         headers={'Content-Type': 'application/json'}).data.decode('utf-8'))
        self.assertEquals(result['status'], "error")
        self.assertEquals(result['info'], "invalid or missing date")

    def test_put_syschange_missing_date(self):
        """test the put sys change API function with an invalid date"""
        result = json.loads(self.app.put('/api/v1.0.0/system_change/1/add_base',
                                         data=json.dumps({
                                             'quantity': 12.3
                                         }),
                                         headers={'Content-Type': 'application/json'}).data.decode('utf-8'))
        self.assertEquals(result['status'], "error")
        self.assertEquals(result['info'], "invalid or missing date")

    def test_put_syschange_invalid_change_type(self):
        """test the put sys change API function with a non existing change type"""
        result = json.loads(self.app.put('/api/v1.0.0/system_change/1/nonexisting',
                                         data=json.dumps({
                                             'time': '2017-04-17T13:24:00Z',
                                             'quantity': 12.3
                                         }),
                                         headers={'Content-Type': 'application/json'}).data.decode('utf-8'))
        self.assertEquals(result['status'], "error")
        self.assertEquals(result['info'], "change type does not exist")

    def test_put_syschange_invalid_float_instead_of_int(self):
        """test the put sys change API function with a float instead of integer"""
        result = json.loads(self.app.put('/api/v1.0.0/system_change/1/harvest_fish',
                                         data=json.dumps({
                                             'time': '2017-04-17T13:24:00Z',
                                             'quantity': 12.3,
                                             'subtype': 1
                                         }),
                                         headers={'Content-Type': 'application/json'}).data.decode('utf-8'))
        self.assertEquals(result['status'], "error")
        self.assertEquals(result['info'], "invalid quantity")


    def test_put_syschange_no_quantity_error(self):
        """test the put sys change API function"""
        result = json.loads(self.app.put('/api/v1.0.0/system_change/1/add_base',
                                         data=json.dumps({
                                             'time': '2017-04-17T13:24:00Z'
                                         }),
                                         headers={'Content-Type': 'application/json'}).data.decode('utf-8'))
        self.assertEquals(result['status'], "error")
        self.assertEquals(result['info'], "missing quantity")

    def test_put_syschange_no_quantity_ok(self):
        """test the put sys change API function"""
        result = json.loads(self.app.put('/api/v1.0.0/system_change/1/reproduction',
                                         data=json.dumps({
                                             'time': '2017-04-17T13:24:00Z'
                                         }),
                                         headers={'Content-Type': 'application/json'}).data.decode('utf-8'))
        self.assertEquals(result['status'], "ok")


    def test_put_syschange_decimal(self):
        """test the put sys change API function for decimal types"""
        result = json.loads(self.app.put('/api/v1.0.0/system_change/1/add_base',
                                         data=json.dumps({
                                             'time': '2017-04-17T13:24:00Z',
                                             'quantity': 12.3
                                         }),
                                         headers={'Content-Type': 'application/json'}).data.decode('utf-8'))
        self.assertEquals(result['status'], "ok")

        # updated state of the database
        result = json.loads(self.app.get('/api/v1.0.0/system_changes/1/add_base').data.decode('utf-8'))
        self.assertEquals(result['change_type'], "add_base")
        self.assertEquals(len(result['changes']), 1)
        change = result['changes'][0]
        self.assertEquals(change['quantity'], 12.3)
        self.assertEquals(change['time'], '2017-04-17T13:24:00Z')

    def test_put_syschange_with_subtype_no_subtype(self):
        """test the put sys change API function for integer types"""
        result = json.loads(self.app.put('/api/v1.0.0/system_change/1/add_fish',
                                         data=json.dumps({
                                             'time': '2017-04-17T13:24:00Z',
                                             'quantity': 3
                                         }),
                                         headers={'Content-Type': 'application/json'}).data.decode('utf-8'))
        self.assertEquals(result['status'], "error")
        self.assertEquals(result['info'], "missing subtype")

    def test_put_syschange_integer_and_subtype(self):
        """test the put sys change API function for integer types"""
        result = json.loads(self.app.put('/api/v1.0.0/system_change/1/add_fish',
                                         data=json.dumps({
                                             'time': '2017-04-17T13:24:00Z',
                                             'quantity': 3,
                                             'subtype': 1
                                         }),
                                         headers={'Content-Type': 'application/json'}).data.decode('utf-8'))
        self.assertEquals(result['status'], "ok")

        # updated state of the database
        result = json.loads(self.app.get('/api/v1.0.0/system_changes/1/add_fish').data.decode('utf-8'))
        self.assertEquals(result['change_type'], "add_fish")
        self.assertEquals(len(result['changes']), 1)
        change = result['changes'][0]
        self.assertEquals(change['quantity'], 3)
        self.assertEquals(change['time'], '2017-04-17T13:24:00Z')
        self.assertEquals(change['subtype'], 1)

    def test_put_syschange_none_type(self):
        """test the put sys change API function for the none type"""
        result = json.loads(self.app.put('/api/v1.0.0/system_change/1/reproduction',
                                         data=json.dumps({
                                             'time': '2017-04-17T13:24:00Z'
                                         }),
                                         headers={'Content-Type': 'application/json'}).data.decode('utf-8'))
        self.assertEquals(result['status'], "ok")

        # updated state of the database
        result = json.loads(self.app.get('/api/v1.0.0/system_changes/1/reproduction').data.decode('utf-8'))
        self.assertEquals(result['change_type'], "reproduction")
        self.assertEquals(len(result['changes']), 1)
        change = result['changes'][0]
        self.assertEquals(change['time'], '2017-04-17T13:24:00Z')


if __name__ == '__main__':
    SUITE = []
    SUITE.append(unittest.TestLoader().loadTestsFromTestCase(APITest))
    if len(sys.argv) > 1 and sys.argv[1] == 'xml':
      xmlrunner.XMLTestRunner(output='test-reports').run(unittest.TestSuite(SUITE))
    else:
      unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(SUITE))
