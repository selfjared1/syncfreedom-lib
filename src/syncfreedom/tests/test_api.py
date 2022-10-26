import unittest
from src.syncfreedom.client import SyncFreedomQuickBooks
from configparser import ConfigParser

configur = ConfigParser()
configur.read('config.ini')

class APITest(unittest.TestCase):

    def setUp(self):
        company_id = configur['SYNCFREEDOM_TEST_COMPANY']['company_id']
        self.assertIsNot(company_id, 'test_company_realm_id')
        self.company_id = company_id
        self.qb = SyncFreedomQuickBooks(self.company_id)
        self.assertEquals(configur['ENVIRONMENT_INFO']['sync_freedom_url'], 'http://127.0.0.1:8000')

    def test_account(self):
        print('yeppee')
        self.assertIsInstance(self.qb, SyncFreedomQuickBooks)
        # self.assertEquals(r.status_code, 200)
