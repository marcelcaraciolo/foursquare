import unittest
import urllib
from foursquare import OAuthHandler, API, BasicAuthHandler, FoursquareError
from models import Tip


class TestAuthentication(unittest.TestCase):
    CLIENT_ID = 'YOUR_CLIENT_ID'
    CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
    REDIRECT_URI = 'YOUR_CALLBACK'

    def _test_create_OAuthHandler(self):
        auth = OAuthHandler(TestAuthentication.CLIENT_ID,
                         TestAuthentication.CLIENT_SECRET,
                        TestAuthentication.REDIRECT_URI)
        self.assertEquals(auth._client_id, TestAuthentication.CLIENT_ID)
        self.assertEquals(auth._client_secret, TestAuthentication.CLIENT_SECRET)
        self.assertEquals(auth.callback, TestAuthentication.REDIRECT_URI)

    def _test_get_authorization_url(self):
        auth = OAuthHandler(TestAuthentication.CLIENT_ID, TestAuthentication.CLIENT_SECRET,
           TestAuthentication.REDIRECT_URI)
        self.assertEquals(auth.get_authorization_url(),
            ('https://foursquare.com/oauth2/authenticate?redirect_uri=%s' +
            '&response_type=code&client_id=%s')
            % (urllib.quote(self.REDIRECT_URI).replace('/', '%2F'), self.CLIENT_ID)
        )

    def _test_get_access_token(self):
        auth = OAuthHandler(TestAuthentication.CLIENT_ID, TestAuthentication.CLIENT_SECRET,
            TestAuthentication.REDIRECT_URI)
        code = 'YOUR_CODE'
        self.assert_(auth.get_access_token(code) is not None)


class TestAPI(unittest.TestCase):
    CLIENT_ID = 'YOUR_CLIENT_ID'
    CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
    REDIRECT_URI = 'YOUR_CALLBACK'

    def setUp(self):
        self.auth = OAuthHandler(TestAuthentication.CLIENT_ID,
                                TestAuthentication.CLIENT_SECRET,
                                TestAuthentication.REDIRECT_URI)
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
        self.assertEquals('Burburinho', result[0].name)

        #Without authentication
        basic_auth = BasicAuthHandler(TestAuthentication.CLIENT_ID,
                                TestAuthentication.CLIENT_SECRET,
                                TestAuthentication.REDIRECT_URI)
        api = API(basic_auth)
        result = api.venues_search(query='Burburinho', ll='-8.063542,-34.872891')
        self.assertEquals('Burburinho', result[0].name)
        self.assertRaises(FoursquareError, api.venues_tips, id='4bb0e776f964a52099683ce3')

    def test_venues(self):
        api = API(self.auth)
        self.assertEquals('Burburinho', api.venues(id='4bb0e776f964a52099683ce3').name)

    def test_venues_tips(self):
        api = API(self.auth)
        r = api.venues_tips(id='4bb0e776f964a52099683ce3')
        self.assert_(isinstance(r[0], Tip))
        r = api.venues_tips(id='40a55d80f964a52020f31ee3', limit=200)
        self.assert_(isinstance(r[0], Tip))
        self.assertEquals(len(r), 170)

unittest.main()
