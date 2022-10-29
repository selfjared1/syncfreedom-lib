from rauth.session import OAuth2Session

class SyncFreedomOAuth2Session(OAuth2Session):

    def __init__(self,
                 access_token,
                 service=None,
                 *args,
                 **kwargs):
        self.access_token_key = 'access_token'
        super(SyncFreedomOAuth2Session, self).__init__(access_token=access_token, *args, **kwargs)

