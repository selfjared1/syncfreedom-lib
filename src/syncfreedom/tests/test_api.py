import unittest
from src.syncfreedom.client import SyncFreedomQuickBooks
from quickbooks.objects.account import Account
from configparser import ConfigParser
import os

configur = ConfigParser()
configur.read(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.ini'))

class APITest(unittest.TestCase):

    def setUp(self):
        company_id = configur['SYNCFREEDOM_TEST_COMPANY']['company_id']
        credentials = configur['SYNCFREEDOM_CREDENTIALS']
        self.assertIsNot(company_id, 'test_company_realm_id')
        self.company_id = company_id
        print(company_id)
        self.qb = SyncFreedomQuickBooks(company_id=self.company_id, credentials=credentials)
        self.assertEquals(configur['ENVIRONMENT_INFO']['sync_freedom_url'], 'http://127.0.0.1:8000')

    def test_account(self):
        self.assertIsInstance(self.qb, SyncFreedomQuickBooks)
        account = Account()
        account.FullyQualifiedName = "test"

        self.assertEquals(str(account), "test")

    def test_to_ref(self):
        account = Account()
        account.FullyQualifiedName = "test"
        account.Id = 12

        ref = account.to_ref()

        self.assertEquals(ref.name, "test")
        self.assertEquals(ref.type, "Account")
        self.assertEquals(ref.value, 12)

    def test_valid_object_name(self):
        account = Account()
        result = self.qb.isvalid_object_name(account.qbo_object_name)
        self.assertTrue(result)
