from requests_oauthlib import OAuth1Session

class WordpressAPI(object):
    def __init__(self, testing=None):
        if testing is None:
            raise ValueError("WordpressAPI requires `testing` kwarg")
        self.testing = testing
        if testing:
            self.base_url = 'https://test.balloon-juice.com/index.php/wp-json'
            self.client_key = '3Xh5uQ3FTY2X'
            self.client_secret = 'ZUo6GuQovNUFhFmP4XNOBsnvtphs5O1cEOPolpcBx1GjmBh9'
            self.resource_owner_key = u'rrg8d6gIE6Jx0Ghs6VYpBcaL'
            self.resource_owner_secret = u'tU5hFTJNmUSm2v631ykw5X4g3IEHDBMBUV6XLxw7kuGHu8cM'
            self.oauth = OAuth1Session(
                    self.client_key,
                    client_secret=self.client_secret,
                    resource_owner_key=self.resource_owner_key,
                    resource_owner_secret=self.resource_owner_secret
            )
        else:
            raise NotImplementedError()

    def get(self, path):
        url = self._make_url(path)
        return self.oauth.get(url)

    def post(self, path, **kwargs):
        url = self._make_url(path)
        return self.oauth.post(url, **kwargs)

    def _make_url(self, path):
        return self.base_url + path
