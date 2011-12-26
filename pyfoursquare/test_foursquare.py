import unittest

from foursquare import OAuthHandler, API


class TestAuthentication(unittest.TestCase):
    CLIENT_ID = 'YOUR_CLIENT_ID'
    CLIENT_SECRET = 'YOUR_CLIENT_SECRET'

    def _test_create_OAuthHandler(self):
        auth = OAuthHandler(TestAuthentication.CLIENT_ID, TestAuthentication.CLIENT_SECRET,
            'YOUR_CALLBACK')
        self.assertEquals(auth._client_id, TestAuthentication.CLIENT_ID)
        self.assertEquals(auth._client_secret, TestAuthentication.CLIENT_SECRET)
        self.assertEquals(auth.callback, 'YOUR_CALLBACK')

    def _test_get_authorization_url(self):
        auth = OAuthHandler(TestAuthentication.CLIENT_ID, TestAuthentication.CLIENT_SECRET,
            'YOUR_CALLBACK')
        self.assertEquals(auth.get_authorization_url(),
            'https://foursquare.com/oauth2/authenticate?redirect_uri=YOUR_CALLBACK' +
            '&response_type=code&client_id=YOUR_CLIENT_ID'
        )

    def _test_get_access_token(self):
        auth = OAuthHandler(TestAuthentication.CLIENT_ID, TestAuthentication.CLIENT_SECRET,
            'YOUR_CALLBACK')
        code = 'YOUR_CODE'
        self.assert_(auth.get_access_token(code) is not None)


class TestAPI(unittest.TestCase):
    CLIENT_ID = 'YOUR_CLIENT_ID'
    CLIENT_SECRET = 'YOUR_CLIENT_SECRET'

    def setUp(self):
        self.auth = OAuthHandler(TestAuthentication.CLIENT_ID,
                                TestAuthentication.CLIENT_SECRET,
                                'YOUR_CALLBACK')
        self.auth.set_access_token('YOUR_ACCESS_TOKEN')

    def test_create_api(self):
        api = API(self.auth)
        self.assertEquals(api.auth, self.auth)
        self.assertEquals(api.host, 'api.foursquare.com')
        self.assertEquals(api.api_root, '/v2')
        self.assertEquals(api.retry_errors, None)
        self.assertEquals(api.retry_count, 0)
        self.assertEquals(api.retry_delay, 0)

    def test_venues_search(self):
        api = API(self.auth)
        result = api.venues_search(query='Burburinho', ll='-8.063542,-34.872891')
        print result
        print dir(result[0])
        print result[0].name

    def _test_venues(self):
        api = API(self.auth)
        print api.venues(id='4bb0e776f964a52099683ce3')

    def _test_venues_tips(self):
        api = API(self.auth)
        print api.venues_tips(id='4bb0e776f964a52099683ce3')

unittest.main()
