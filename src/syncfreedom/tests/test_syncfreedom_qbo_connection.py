import unittest
from unittest.mock import patch, Mock
from src.syncfreedom.client import SyncFreedomQBOConnection, SyncFreedomQBOConnections
import json

class TestSyncFreedomQBOConnection(unittest.TestCase):
    def setUp(self):
        self.credentials = {'username': 'test_user', 'password': 'test_pass'}
        self.company_id = '123'

        # Mock response data
        self.mock_response_data = {
            'count': 1,
            'results': [{
                'qbo_company_name': 'Test Company',
                'last_refreshed_dt': '2022-01-01',
                'access_token': 'access_token_123',
                'refresh_token': 'refresh_token_123',
                'x_refresh_token_expires_in_seconds': 3600,
                'access_token_expires_in_seconds': 3600
            }]
        }

    @patch('src.syncfreedom.client.requests.get')
    def test_successful_initialization(self, mock_get):
        # Setting up the mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = json.dumps(self.mock_response_data)
        mock_get.return_value = mock_response

        # Initializing the SyncFreedomQBOConnection object
        connection = SyncFreedomQBOConnection(self.company_id, self.credentials)

        # Verifying that the object is correctly initialized
        self.assertEqual(connection.qbo_company_name, 'Test Company')
        self.assertEqual(connection.last_refresh_dt, '2022-01-01')
        self.assertEqual(connection.access_token, 'access_token_123')
        self.assertEqual(connection.refresh_token, 'refresh_token_123')
        self.assertEqual(connection.x_refresh_token_expires_in_seconds, 3600)
        self.assertEqual(connection.access_token_expires_in_seconds, 3600)


class TestSyncFreedomQBOConnections(unittest.TestCase):
    def setUp(self):
        self.credentials = {'username': 'test_user', 'password': 'test_pass'}

        # Mock response data for the API
        self.mock_response_data = {
            'count': 2,
            'results': [
                {
                    'realm_id': '123',
                    'qbo_company_name': 'Test Company 1',
                    'last_refreshed_dt': '2022-01-01',
                    'access_token': 'access_token_123',
                    'refresh_token': 'refresh_token_123',
                    'x_refresh_token_expires_in_seconds': 3600,
                    'access_token_expires_in_seconds': 3600
                },
                {
                    'realm_id': '456',
                    'qbo_company_name': 'Test Company 2',
                    'last_refreshed_dt': '2022-01-02',
                    'access_token': 'access_token_456',
                    'refresh_token': 'refresh_token_456',
                    'x_refresh_token_expires_in_seconds': 7200,
                    'access_token_expires_in_seconds': 7200
                }
            ]
        }

    @patch('src.syncfreedom.client.requests.get')
    def test_get_qbo_connections(self, mock_get):
        # Setting up the mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = json.dumps(self.mock_response_data)
        mock_get.return_value = mock_response

        # Initializing the SyncFreedomQBOConnections object
        connections = SyncFreedomQBOConnections(self.credentials)

        # Verifying that the object is correctly initialized
        self.assertEqual(len(connections.qbo_connections), 2)
        self.assertIsInstance(connections.qbo_connections[0], SyncFreedomQBOConnection)
        self.assertIsInstance(connections.qbo_connections[1], SyncFreedomQBOConnection)
        self.assertEqual(connections.qbo_connections[0].qbo_company_name, 'Test Company 1')
        self.assertEqual(connections.qbo_connections[1].qbo_company_name, 'Test Company 2')


