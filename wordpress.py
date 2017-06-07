from requests_oauthlib import OAuth1Session

import config
import json


class WordpressAPI(object):
    def __init__(self, environment=None):
        if environment is None or environment not in config.WORDPRESS:
            raise ValueError("Bad or missing `environment` kwarg")
        self.environment = environment
        get_value = lambda k: config.WORDPRESS[environment][k]
        self.base_url = get_value('base_url')
        self.client_key = get_value('client_key')
        self.client_secret = get_value('client_secret')
        self.resource_owner_key = get_value('resource_owner_key')
        self.resource_owner_secret = get_value('resource_owner_secret')
        self.oauth = OAuth1Session(
                self.client_key,
                client_secret=self.client_secret,
                resource_owner_key=self.resource_owner_key,
                resource_owner_secret=self.resource_owner_secret
        )

    def get(self, path, **kwargs):
        url = self._make_url(path)
        return self.oauth.get(url, **kwargs)

    def post(self, path, **kwargs):
        url = self._make_url(path)
        return self.oauth.post(url, **kwargs)

    def verify_nym(self, nym, email):
        payload = {'author_email': email}
        r = self.get('/wp/v2/comments', params=payload)
        results = json.loads(r.text)
        if any([result for result in results if result['author_name']==nym]):
            return True
        return False

    def _make_url(self, path):
        return self.base_url + path
