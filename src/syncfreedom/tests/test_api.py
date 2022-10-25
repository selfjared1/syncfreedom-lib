import unittest
from src.syncfreedom.client import SyncFreedomQuickBooks
from configparser import ConfigParser

configur = ConfigParser()
configur.read('config.ini')

class APITest(unittest.TestCase):

    def setUp(self):
        company_id = configur['SYNCFREEDOM_CREDENTIALS']['company_id']
        self.assertIsNot(company_id, 'test_company_realm_id')
        self.company_id = company_id
        self.qb = SyncFreedomQuickBooks.from_company_id(self.company_id)

    def test_object_creation(self):
        print('yeppee')
        self.assertIsInstance(self.qb, SyncFreedomQuickBooks)
        # self.assertEquals(r.status_code, 200)
