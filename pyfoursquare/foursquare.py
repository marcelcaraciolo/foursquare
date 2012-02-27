# -*- coding: utf-8 -*-


"""
A Python interface for the Foursquare API.

If you are looking for a complete foursquare-APIv2 reference, go to

    <http://developer.foursquare.com/docs/>


https://github.com/marcelcaraciolo/foursquare


"""

import urllib
import time
import json as simplejson
import httplib
import re
from datetime import datetime
from models import ModelFactory


re_path_template = re.compile('{\w+}')


class FoursquareError(Exception):
    """ Foursquare execution """

    def __init__(self, reason, response=None):
        self.reason = unicode(reason)
        self.response = response

    def __str__(self):
        return self.reason


def convert_to_utf8_str(arg):
    # written by Michael Norton (http://docondev.blogspot.com/)
    if isinstance(arg, unicode):
        arg = arg.encode('utf-8')
    elif not isinstance(arg, str):
        arg = str(arg)
    return arg


def bind_api(**config):

    class APIMethod(object):
        path = config['path']
        payload_type = config.get('payload_type', None)
        payload_list = config.get('payload_list', False)
        allowed_param = config.get('allowed_param', [])
        method = config.get('method', 'GET')
        require_auth = config.get('require_auth', False)

        def __init__(self, api, args, kwargs):
            #It must be authenticated for method calls
            if self.require_auth and not hasattr(api.auth, 'access_token'):
                raise FoursquareError('Authentication required!')

            self.api = api
            self.post_data = kwargs.pop('post_data', None)
            self.retry_count = kwargs.pop('retry_count', api.retry_count)
            self.retry_delay = kwargs.pop('retry_delay', api.retry_delay)
            self.retry_errors = kwargs.pop('retry_errors', api.retry_errors)
            self.headers = kwargs.pop('headers', {})
            self.build_parameters(args, kwargs)

            self.api_root = api.api_root

            #Perform any path variable substitution
            self.build_path()

            self.scheme = 'https://'

            self.host = api.host

        def build_path(self):
            for variable in re_path_template.findall(self.path):
                name = variable.strip('{}')

                try:
                    value = urllib.quote(self.parameters[name])
                except KeyError:
                    raise FoursquareError('No parameter value found for \
                                            path variable: %s' % name)
                del self.parameters[name]

                self.path = self.path.replace(variable, value)

        def build_parameters(self, args, kwargs):
            self.parameters = {}
            for idx, arg in enumerate(args):
                if arg is None:
                    continue

                try:
                    self.parameters[self.allowed_param[idx]] = convert_to_utf8_str(arg)
                except IndexError:
                    raise FoursquareError('Too many parameters supplied!')

            for k, arg in kwargs.items():
                if arg is None:
                    continue
                if k in self.parameters:
                    raise FoursquareError('Multiple values for parameter %s supplied!' % k)

                self.parameters[k] = convert_to_utf8_str(arg)

        def execute(self):
            #Build the request URL
            url = self.api_root + self.path

            #Apply authentication
            if self.api.auth:
                url = '%s?%s' % (url, self.api.auth.apply_auth())

            self.parameters['v'] = datetime.now().strftime('%Y%m%d')

            if len(self.parameters):
                if self.api.auth:
                    url = '%s&%s' % (url, urllib.urlencode(self.parameters))
                else:
                    url = '%s?%s' % (url, urllib.urlencode(self.parameters))

            #Continue attempting request until successful
            #or maximum number of retries is reached
            retries_performed = 0
            while retries_performed < self.retry_count + 1:
                #Open the connection
                conn = httplib.HTTPSConnection(self.host)
                #Execute the request
                try:
                    conn.request(self.method, url, headers=self.headers, body=self.post_data)
                    resp = conn.getresponse()
                except Exception, e:
                    raise FoursquareError('Failed to send request: %s' % e)

                #Exit request loop if non-retry error code
                if self.retry_errors:
                    if resp.status not in self.retry_errors:
                        break
                    else:
                        if resp.status == 200:
                            break

                # Sleep before retrying request again
                time.sleep(self.retry_delay)
                retries_performed += 1

            # If an error was returned, throw an exception
            self.api.last_response = resp
            if resp.status != 200:
                try:
                    error_msg = self.api.parser.parse_error(resp.read())
                except Exception:
                    error_msg = "Foursquare error response: status code = %s" % resp.status
                raise FoursquareError(error_msg, resp)

            # Parse the response payload
            result = self.api.parser.parse(self, resp.read())
            conn.close()

            return result

    def _call(api, *args, **kargs):

        method = APIMethod(api, args, kargs)
        return method.execute()

    return _call


class BasicAuthHandler(object):
    """
    For non-OAuth authentication required method requests
    """
    def __init__(self, client_id, client_secret, callback=None):
        self._client_id = client_id
        self._client_secret = client_secret
        self.callback = callback

    def apply_auth(self):
        return 'client_id=%s&client_secret=%s' % (self._client_id, self._client_secret)


class OAuthHandler(BasicAuthHandler):
    """ OAuth authentication handler """

    OAUTH_HOST = 'foursquare.com'
    OAUTH_ROOT = '/oauth2/'

    def __init__(self, client_id, client_secret, callback=None):
        BasicAuthHandler.__init__(self, client_id, client_secret, callback)

    def _get_oauth_url(self, endpoint):
        return 'https://' + self.OAUTH_HOST + self.OAUTH_ROOT + endpoint

    def apply_auth(self):
        return "oauth_token=" + self.access_token

    def urlencode(self, query):
        return urllib.urlencode(query)

    def get_authorization_url(self):
        """Get the authorization URL to redirect the user"""
        url = self._get_oauth_url('authenticate')
        query = {
            'client_id': self._client_id,
            'response_type': 'code',
            'redirect_uri': self.callback
        }
        query_str = self.urlencode(query)

        return url + '?' + query_str

    def set_request_token(self, key, secret):
        self._client_id = key
        self._client_secret = secret

    def set_access_token(self, access_token):
        self.access_token = access_token

    def get_access_token(self, verifier=None):
        """
        After user has authorized the request token, get access token
        with user supplied verifier.
        """
        try:
            url = self._get_oauth_url('access_token')

            #build request
            query = {
                'client_id': self._client_id,
                'client_secret': self._client_secret,
                'grant_type': 'authorization_code',
                'redirect_uri': self.callback,
                'code': str(verifier)
            }

            query_str = self.urlencode(query)
            request = url + '?' + query_str

            #send request
            resp = urllib.urlopen(request)
            json = simplejson.loads(resp.read())

            self.access_token = json['access_token']

            return self.access_token

        except Exception, e:
            raise FoursquareError(e)


class JSONParser(object):

    payload_format = 'json'

    def parse(self, method, payload):
        try:
            json = simplejson.loads(payload)
        except Exception, e:
            raise FoursquareError('Failed to parse JSON payload: %s' % e)

        needsCursors = 'offset 'in method.parameters
        if needsCursors and isinstance(json, dict) \
            and 'previous_cursor' in json and 'next_cursor' in json:
            cursors = json['previous_cursor'], json['next_cursor']
            return json, cursors
        else:
            return json

    def parse_error(self, payload):
        error = simplejson.loads(payload)
        meta = error.get('meta')
        msg = ""
        if meta:
            if 'errorType' in meta:
                msg += meta['errorType']

            if 'errorDetail' in meta:
                msg = msg + ': ' + meta['errorDetail']
        return msg


class ModelParser(JSONParser):

    def __init__(self, model_factory=None):
        JSONParser.__init__(self)
        self.model_factory = model_factory or ModelFactory

    def parse(self, method, payload):
        try:
            if method.payload_type is None:
                return
            model = getattr(self.model_factory, method.payload_type)
        except AttributeError:
            raise FoursquareError('No model for this payload type: %s' % method.payload_type)

        json = JSONParser.parse(self, method, payload)

        if method.payload_list and method.payload_type not in ['venues']:
            result = model.parse_list(method.api, json['response'][method.payload_type]['items'])
        elif method.payload_list:
            #Search Result
            result = model.parse_list(method.api, json['response'][method.payload_type])
        else:
            result = model.parse(method.api, json['response'][method.payload_type])
        return result

        if isinstance(json, tuple):
            json, cursors = json
        else:
            cursors = None

        if method.payload_list:
            result = model.parse_list(method.api, json)
        else:
            result = model.parse(method.api, json)

        if cursors:
            return result, cursors


class API(object):
    """Foursquare API """
    def __init__(self, auth_handler=None, host='api.foursquare.com',
        api_root='/v2', retry_errors=None, retry_delay=0,
        retry_count=0):
        self.auth = auth_handler
        self.host = host
        self.api_root = api_root
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.retry_errors = retry_errors
        self.parser = ModelParser()

    """ venues/search """
    venues_search = bind_api(
        path='/venues/search',
        payload_type='venues', payload_list=True,
        allowed_param=['ll', 'llAcc', 'alt', 'altAcc', 'query',
                         'limit', 'intent', 'radius']
    )

    """ venues """
    venues = bind_api(
        path='/venues/{id}',
        payload_type='venue', payload_list=False,
        allowed_param=['id'],
        require_auth=True
    )

    """ venues/tips """
    venues_tips = bind_api(
        path='/venues/{id}/tips',
        payload_type='tips', payload_list=True,
        allowed_param=['id', 'sort', 'limit', 'offset'],
        require_auth=True

    )

    """ tips """
    tips = bind_api(
        path='/tips/{id}',
        payload_type='tips', payload_list=True,
        allowed_param=['id'],
        require_auth=True

    )
