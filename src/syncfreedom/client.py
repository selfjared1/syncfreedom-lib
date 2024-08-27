from quickbooks.client import QuickBooks
import requests
from base64 import b64encode
import json
from intuitlib.client import AuthClient
from intuitlib.utils import send_request
from intuitlib.utils import get_discovery_doc
from future.moves.urllib.parse import urlencode
from .session import SyncFreedomOAuth2Session

sync_freedom_url = 'https://syncfreedom.com'

class Environments(object):
    SANDBOX = 'sandbox'
    PRODUCTION = 'production'

class SyncFreedomQBOConnection():
    """
    You set your credentials inside a dictionary or an ini file.  Use the keys 'username' and 'password'
    This class is a modification of the QBOConnection class located in the python-quickbooks Pypi package
    You can find documentation on the python-quickbooks Pypi package here: https://pypi.org/project/python-quickbooks/
    Or go to the github page here: https://github.com/ej2/python-quickbooks
    """

    def __init__(self, company_id, credentials=None, qbo_connection_dict=None):
        self.realm_id = company_id
        self.credentials = credentials
        if credentials:
            self._get_qbo_connection()
        elif qbo_connection_dict:
            self._from_dict(qbo_connection_dict)
        else:
            raise ValueError('Either credentials or qbo_connection_dict must be provided')

    @property
    def company_id(self):
        return self.realm_id

    def _get_qbo_connection(self):
        auth_str = bytes(str(self.credentials['username']) + ':' + str(self.credentials['password']), "ascii")
        user_and_pass = b64encode(auth_str).decode("ascii")
        headers = {'Authorization': 'Basic %s' % user_and_pass}
        response = requests.get(sync_freedom_url + '/api/qbo_connection',
                                params={'realm_id': self.realm_id},
                                headers=headers)
        assert response.status_code == 200
        response_dict = json.loads(response.text)
        assert response_dict['count'] == 1, f"""Company Id {self.realm_id} returned {response_dict['count']} results"""
        qbo_connection_dict = response_dict['results'][0]
        self.__setattr__('qbo_company_name',qbo_connection_dict['qbo_company_name'])
        self.__setattr__('last_refresh_dt', qbo_connection_dict['last_refreshed_dt'])
        self.__setattr__('access_token', qbo_connection_dict['access_token'])
        self.__setattr__('refresh_token', qbo_connection_dict['refresh_token'])
        self.__setattr__('x_refresh_token_expires_in_seconds', qbo_connection_dict['x_refresh_token_expires_in_seconds'])
        self.__setattr__('access_token_expires_in_seconds', qbo_connection_dict['access_token_expires_in_seconds'])

    def _from_dict(self, qbo_connection_dict):
        try:
            self.__setattr__('qbo_company_name', qbo_connection_dict['qbo_company_name'])
            self.__setattr__('last_refresh_dt', qbo_connection_dict['last_refreshed_dt'])
            self.__setattr__('access_token', qbo_connection_dict['access_token'])
            self.__setattr__('refresh_token', qbo_connection_dict['refresh_token'])
            self.__setattr__('x_refresh_token_expires_in_seconds',
                             qbo_connection_dict['x_refresh_token_expires_in_seconds'])
            self.__setattr__('access_token_expires_in_seconds', qbo_connection_dict['access_token_expires_in_seconds'])
        except Exception as e:
            raise e

class SyncFreedomQBOConnections():
    """
        You set your credentials inside a dictionary or an ini file.  Use the keys 'username' and 'password'
        This class is to manage the list of QBOConnections on SyncFreedom.com
        """
    def __init__(self, credentials):
        self.credentials = credentials
        self.qbo_connections = []
        self._get_qbo_connections()

    def _get_qbo_connections(self):
        auth_str = bytes(str(self.credentials['username']) + ':' + str(self.credentials['password']), "ascii")
        user_and_pass = b64encode(auth_str).decode("ascii")
        headers = {'Authorization': 'Basic %s' % user_and_pass}
        url = sync_freedom_url + '/api/qbo_connections'

        while url:
            response = requests.get(url, headers=headers)
            assert response.status_code == 200
            response_dict = json.loads(response.text)
            assert response_dict['count'] > 0, "You have no QBO Connections on SyncFreedom.com"
            for result in response_dict['results']:
                qbo_connection = SyncFreedomQBOConnection(result['realm_id'], qbo_connection_dict=result)
                self.qbo_connections.append(qbo_connection)

            url = response_dict.get('next')


    @property
    def company_name_list(self):
        return [qbo_connection.qbo_company_name for qbo_connection in self.qbo_connections]

    def get_from_company_name(self, company_name):
        qbo_connection = next((qbo_connection for qbo_connection in self.qbo_connections if qbo_connection.qbo_company_name.lower() == company_name.lower()), None)
        if qbo_connection is None:
            raise ValueError('Company name not found')
        else:
            return qbo_connection

    def get_from_realm_id(self, realm_id):
        qbo_connection = next((qbo_connection for qbo_connection in self.qbo_connections if
                               qbo_connection.realm_id == realm_id), None)
        if qbo_connection is None:
            raise ValueError('Company realm_id not found')
        else:
            return qbo_connection


class SyncFreedomAuthClient(AuthClient):
    """Leverages OAuth 2.0 Connect flows on SyncFreedom.com to get access to User Info API and Accoutning APIs
    """
    # todo: need to create this authclient without client_id, client_secret, etc. and then plug it into kwargs for SyncFreedomQuickBooks
    def __init__(self, qbo_connection, environment):
        super(SyncFreedomAuthClient, self).__init__(environment=environment,
                                                    realm_id=qbo_connection.realm_id,
                                                    client_id=None,
                                                    client_secret=None,
                                                    redirect_uri=None,
                                                    state_token=None,
                                                    access_token=None,
                                                    refresh_token=None,
                                                    id_token=None,
                                                    )

        self.environment = environment

        # Discovery doc contains endpoints based on environment specified
        discovery_doc = get_discovery_doc(self.environment, session=self)
        self.auth_endpoint = discovery_doc['authorization_endpoint']
        self.token_endpoint = discovery_doc['token_endpoint']
        self.revoke_endpoint = discovery_doc['revocation_endpoint']
        self.issuer_uri = discovery_doc['issuer']
        self.jwks_uri = discovery_doc['jwks_uri']
        self.user_info_url = discovery_doc['userinfo_endpoint']

        # response values
        self.realm_id = qbo_connection.realm_id

        self.access_token = qbo_connection.access_token
        self.expires_in = qbo_connection.access_token_expires_in_seconds
        self.refresh_token = qbo_connection.refresh_token
        self.x_refresh_token_expires_in = qbo_connection.x_refresh_token_expires_in_seconds
        self.id_token = None


    def get_authorization_url(self, scopes, state_token=None):
        return 'not_supported'

    def get_bearer_token(self, auth_code, realm_id=None):
        pass

    def refresh(self, refresh_token=None):
        """Gets fresh access_token and refresh_token

        :param refresh_token: Refresh Token
        :raises ValueError: if Refresh Token value not specified
        :raises `intuitlib.exceptions.AuthClientError`: if response status != 200
        """

        token = refresh_token or self.refresh_token
        if token is None:
            raise ValueError('Refresh token not specified')

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer {0}'.format(self.access_token)
        }

        body = {
            'grant_type': 'refresh_token',
            'refresh_token': token
        }

        send_request('POST', self.token_endpoint, headers, self, body=urlencode(body), session=self)

    def revoke(self, token=None):
        pass

    def get_user_info(self, access_token=None):
        """Gets User Info based on OpenID scopes specified

        :param access_token: Access token
        :raises ValueError: if Refresh Token or Access Token value not specified
        :raises `intuitlib.exceptions.AuthClientError`: if response status != 200
        :return: Requests object
        """

        token = access_token or self.access_token
        if token is None:
            raise ValueError('Acceess token not specified')

        headers = {
            'Authorization': 'Bearer {0}'.format(token)
        }

        return send_request('GET', self.user_info_url, headers, self, session=self)


class SyncFreedomQuickBooks(QuickBooks):

    def __new__(cls, company_id, credentials, sandbox=False, **kwargs):
        """
        Global is disabled, don't set global client instance.
        You must either set credentials or set qbo_connection for this to work.
        """
        instance = object.__new__(cls)

        if 'company_id' in kwargs:
            instance.company_id = kwargs['company_id']
        else:
            instance.company_id = company_id

        qbo_connection = SyncFreedomQBOConnection(instance.company_id, credentials)
        instance.refresh_token = qbo_connection.refresh_token

        if 'auth_client' in kwargs:
            instance.auth_client = kwargs['auth_client']
        elif sandbox:
            instance.auth_client = SyncFreedomAuthClient(qbo_connection, 'Sandbox')
            instance.sandbox = True
        else:
            instance.auth_client = SyncFreedomAuthClient(qbo_connection, 'Production')
            instance.sandbox = False

        instance.auth_client.access_token = qbo_connection.access_token
        instance.refresh_token = instance._start_session()

        if 'minorversion' in kwargs:
            instance.minorversion = kwargs['minorversion']

        instance.invoice_link = kwargs.get('invoice_link', False)

        if 'verifier_token' in kwargs:
            instance.verifier_token = kwargs.get('verifier_token')

        return instance

    def _start_session(self):
        if self.auth_client.access_token is None:
            self.auth_client.refresh(refresh_token=self.refresh_token)

        self.session = SyncFreedomOAuth2Session(access_token=self.auth_client.access_token)
        if self.auth_client.refresh_token:
            return self.auth_client.refresh_token
        else:
            # todo: better exception handling here
            print('dont have refresh token')
            return None
