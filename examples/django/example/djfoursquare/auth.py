from django.conf import settings


def get_consumer_credentials():
    '''
    Return consumer OAuth credentials
    '''
    return getattr(settings, 'FOURSQUARE_CLIENT_ID', ''), \
        getattr(settings, 'FOURSQUARE_CLIENT_SECRET', ''), \
        getattr(settings, 'FOURSQUARE_CALLBACK', '')
