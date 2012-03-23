# Create your views here.
from pyfoursquare import OAuthHandler, FoursquareError
from django.http import *
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth import logout
from auth import get_consumer_credentials
from utils import get_api


def main(request):
    """
    main view of app, either login page or info page
    """
    # if we haven't authorised yet, direct to login page
    if check_key(request):
        return HttpResponseRedirect(reverse('info'))
    else:
        return render_to_response('djfoursquare/login.html')


def unauth(request):
    """
    logout and remove all session data
    """
    if check_key(request):
        api = get_api(request)
        request.session.clear()
        logout(request)
    return HttpResponseRedirect(reverse('main'))


def info(request):
    """
    display some user info to show we have authenticated successfully
    """
    if check_key(request):
        api = get_api(request)
        user = api.users(id='self')
        print dir(user)
        return render_to_response('djfoursquare/info.html', {'user': user})
    else:
        return HttpResponseRedirect(reverse('main'))


def auth(request):
    client_id, client_secret, callback = get_consumer_credentials()

    # start the OAuth process, set up a handler with our details
    oauth = OAuthHandler(client_id, client_secret, callback)
    # direct the user to the authentication url
    auth_url = oauth.get_authorization_url()
    response = HttpResponseRedirect(auth_url)

    return response


def callback(request):
    verifier = request.GET.get('code')
    client_id, client_secret, callback = get_consumer_credentials()
    oauth = OAuthHandler(client_id, client_secret, callback)

    # get the access token and store
    try:
        oauth.get_access_token(verifier)
    except FoursquareError:
        print 'Error, failed to get access token'
    request.session['oauth_token'] = oauth.access_token
    response = HttpResponseRedirect(reverse('info'))
    return response


def check_key(request):
    """
    Check to see if we already have an access_key stored,
    if we do then we have already gone through
    OAuth. If not then we haven't and we probably need to.
    """
    try:
        access_key = request.session.get('oauth_token', None)
        if not access_key:
            return False
    except KeyError:
        return False
    return True
