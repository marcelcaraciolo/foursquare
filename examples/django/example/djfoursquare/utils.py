import pyfoursquare
from djfoursquare.auth import get_consumer_credentials


def get_api(request):
    client_id, client_secret, callback = get_consumer_credentials()
    # set up and return a foursquare api object
    oauth = pyfoursquare.OAuthHandler(client_id, client_secret, callback)
    access_token = request.session['oauth_token']
    oauth.set_access_token(access_token)
    api = pyfoursquare.API(oauth)
    return api
