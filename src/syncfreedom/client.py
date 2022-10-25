from quickbooks.client import QuickBooks
from quickbooks.client import OAuth2Session
from rauth.session import RauthSession
from configparser import ConfigParser
import requests
from base64 import b64encode
import json
from intuitlib.client import AuthClient
from intuitlib.utils import send_request

from intuitlib.utils import get_discovery_doc
from future.moves.urllib.parse import urlencode

configur = ConfigParser()
configur.read('config.ini')

class Environments(object):
    SANDBOX = 'sandbox'
    PRODUCTION = 'production'

class SyncFreedomQBOConnection():

    def __init__(self, company_id):
        self.realm_id = company_id
        self._get_qbo_connection()

    def _get_qbo_connection(self):
        try:
            credentials = configur['SYNCFREEDOM_CREDENTIALS']
        except Exception as e:
            raise Exception(e)
        auth_str = bytes(str(credentials['username']) + ':' + str(credentials['password']), "ascii")
        user_and_pass = b64encode(auth_str).decode("ascii")
        headers = {'Authorization': 'Basic %s' % user_and_pass}
        response = requests.get('https://syncfreedom.com/api/qbo_connection',
                                params={'realm_id': self.realm_id},
                                headers=headers)
        assert response.status_code, 200
        response_dict = json.loads(response.text)
        assert response_dict['count'], 1
        qbo_connection_dict = response_dict['results'][0]
        self.__setattr__('qbo_company_name',qbo_connection_dict['qbo_company_name'])
        self.__setattr__('last_refresh_dt', qbo_connection_dict['last_refresh_dt'])
        self.__setattr__('access_token', qbo_connection_dict['access_token'])
        self.__setattr__('refresh_token', qbo_connection_dict['refresh_token'])
        self.__setattr__('x_refresh_token_expires_in_seconds', qbo_connection_dict['x_refresh_token_expires_in_seconds'])
        self.__setattr__('access_token_expires_in_seconds', qbo_connection_dict['access_token_expires_in_seconds'])

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

# class SyncFreedomOAuth2Session(OAuth2Session):
#     '''
#             A specialized :class:`~requests.sessions.Session` object, wrapping OAuth
#             2.0 logic.
#
#             This object is utilized by the :class:`OAuth2Service` wrapper but can
#             be used independently of that infrastructure. Essentially this is a loose
#             wrapping around the standard Requests codepath. State may be tracked at
#             this layer, especially if the instance is kept around and tracked via some
#             unique identifier, e.g. access token. Things like request cookies will be
#             preserved between requests and in fact all functionality provided by
#             a Requests' :class:`~requests.sessions.Session` object should be exposed
#             here.
#
#             If you were to use this object by itself you could do so by instantiating
#             it like this::
#
#                 session = OAuth2Session('123', '456', access_token='321')
#
#             You now have a session object which can be used to make requests exactly as
#             you would with a normal Requests :class:`~requests.sessions.Session`
#             instance. This anticipates that the standard OAuth 2.0 flow will be modeled
#             outside of the scope of this class. In other words, if the fully qualified
#             flow is useful to you then this object probably need not be used directly,
#             instead consider using :class:`OAuth2Service`.
#
#             Once the session object is setup, you may start making requests::
#
#                 r = session.get('https://example/com/api/resource',
#                                 params={'format': 'json'})
#                 print r.json()
#
#             :param client_id: Client id, defaults to `None`.
#             :type client_id: str
#             :param client_secret: Client secret, defaults to `None`
#             :type client_secret: str
#             :param access_token: Access token, defaults to `None`.
#             :type access_token: str
#             :param access_token_key: The name of the access token key, defaults to
#                 `'access_token'`.
#             :type access_token_key: str
#             :param service: A back reference to the service wrapper, defaults to
#                 `None`.
#             :type service: :class:`rauth.Service`
#             :param access_token_key: The name of the access token key, defaults to
#                 `'access_token'`.
#             :type access_token_key: str
#             '''
#
#     __attrs__ = RauthSession.__attrs__ + ['client_id',
#                                           'client_secret',
#                                           'access_token']
#
#     def __init__(self,
#                  client_id=None,
#                  client_secret=None,
#                  access_token=None,
#                  service=None,
#                  access_token_key=None
#                  ):
#         super(SyncFreedomOAuth2Session, self).__init__()
#
#         #: Client credentials.
#         self.client_id = client_id
#
#         #: Access token.
#         self.access_token = access_token
#
#         #: Access token key, e.g. 'access_token'.
#         self.access_token_key = access_token_key or 'access_token'
#
#         super(OAuth2Session, self).__init__(service)
#
#     def request(self, method, url, bearer_auth=True, **req_kwargs):
#         '''
#         A loose wrapper around Requests' :class:`~requests.sessions.Session`
#         which injects OAuth 2.0 parameters.
#
#         :param method: A string representation of the HTTP method to be used.
#         :type method: str
#         :param url: The resource to be requested.
#         :type url: str
#         :param bearer_auth: Whether to use Bearer Authentication or not,
#             defaults to `True`.
#         :type bearer_auth: bool
#         :param \*\*req_kwargs: Keyworded args to be passed down to Requests.
#         :type \*\*req_kwargs: dict
#         '''
#         req_kwargs.setdefault('params', {})
#
#         url = self._set_url(url)
#
#         if is_basestring(req_kwargs['params']):
#             req_kwargs['params'] = dict(parse_qsl(req_kwargs['params']))
#
#         if bearer_auth and self.access_token is not None:
#             req_kwargs['auth'] = OAuth2Auth(self.access_token)
#         else:
#             req_kwargs['params'].update({self.access_token_key:
#                                              self.access_token})
#
#         req_kwargs.setdefault('timeout', OAUTH2_DEFAULT_TIMEOUT)
#
#         return super(OAuth2Session, self).request(method, url, **req_kwargs)

class SyncFreedomQuickBooks(QuickBooks):

    def __init__(self):
        super(SyncFreedomQuickBooks, self).__init__()

    def __new__(cls, company_id=None, **kwargs):
        """
        If global is disabled, don't set global client instance.
        """
        if QuickBooks.__use_global:
            if QuickBooks.__instance is None:
                QuickBooks.__instance = object.__new__(cls)
            instance = QuickBooks.__instance
        else:
            instance = object.__new__(cls)

        if 'company_id' in kwargs:
            instance.company_id = kwargs['company_id']
        else:
            instance.company_id = company_id

        qbo_connection = SyncFreedomQBOConnection(instance.company_id)
        instance.refresh_token = qbo_connection.refresh_token

        if 'auth_client' in kwargs:
            instance.auth_client = kwargs['auth_client']
        else:
            instance.auth_client = SyncFreedomAuthClient(qbo_connection, configur['ENVIRONMENT_INFO']['environment'])

            if instance.auth_client.environment == Environments.SANDBOX:
                instance.sandbox = True
            else:
                instance.sandbox = False
            instance.auth_client.access_token = qbo_connection.access_token

        instance.refresh_token = instance._start_session(qbo_connection)

        if 'minorversion' in kwargs:
            instance.minorversion = kwargs['minorversion']

        instance.invoice_link = kwargs.get('invoice_link', False)

        if 'verifier_token' in kwargs:
            instance.verifier_token = kwargs.get('verifier_token')

        return instance

    def _start_session(self):
        if self.auth_client.access_token is None:
            self.auth_client.refresh(refresh_token=self.refresh_token)

        if self.auth_client.refresh_token:
            return self.auth_client.refresh_token
        else:
            # todo: better exeption handling here
            print('dont have refresh token')
            return None


    # @classmethod
    # def from_company_id(cls, company_id):
    #     try:
    #         credentials = configur['SYNCFREEDOM_CREDENTIALS']
    #     except Exception as e:
    #         raise Exception(e)
    #     auth_str = bytes(str(credentials['username']) + ':' + str(credentials['password']), "ascii")
    #     user_and_pass = b64encode(auth_str).decode("ascii")
    #     headers = {'Authorization': 'Basic %s' % user_and_pass}
    #     # r = requests.get('https://syncfreedom.com/api/qbo_connection',
    #     #                  params={'realm_id': company_id},
    #     #                  headers=headers)
    #
    #     #local testing
    #     company_id_local = '4620816365233591830'
    #     response = requests.get('http://127.0.0.1:8000/api/qbo_connection',
    #                      params={'realm_id': str(company_id_local)},
    #                      headers=headers)
    #     assert response.status_code, 200
    #     response_dict = json.loads(response.text)
    #     assert response_dict['count'], 1
    #     qbo_connection_dict = response_dict['results'][0]
    #     print(response)
    #     qb = cls(sandbox=False,
    #         consumer_key=qbo_connection_dict,
    #         consumer_secret="consumer_secret",
    #         access_token="access_token",
    #         access_token_secret="access_token_secret",
    #         company_id="company_id",
    #         callback_url="callback_url",
    #         verbose=True)
    #     qb.sandbox = False
    #     qb.company_id = company_id
    #     qb.consumer_key = None
    #     return qb

if __name__ == '__main__':
    company_id = 123145782634539 #live
    # company_id = '193514608588409'  # local
    qb = SyncFreedomQuickBooks.from_company_id(company_id)