import pyfoursquare as foursquare

# == OAuth2 Authentication ==
#
# This mode of authentication is the required one for Foursquare

# The client id and client secret can be found on your application's Details
# page located at https://foursquare.com/oauth/
client_id = ""
client_secret = ""
callback = ''

auth = foursquare.OauthHandler(client_id, client_secret, callback)

#First Redirect the user who wish to authenticate to.
#It will be create the authorization url for your app
auth_url = auth.get_authorization_url()
print 'Please authorize: ' + auth_url

#If the user accepts, it will be redirected back
#to your registered REDIRECT_URI.
#It will give you a code as
#https://YOUR_REGISTERED_REDIRECT_URI/?code=CODE
code = raw_input('The code: ').strip()

#Now your server will make a request for
#the access token. You can save this
#for future access for your app for this user
access_token = auth.get_access_token(code)
print 'Your access token is ' + access_token

#Now let's create an API
api = foursquare.API(auth)

#Now you can access the Foursquare API!
result = api.venues_search(query='Burburinho', ll='-8.063542,-34.872891')

#You can acess as a Model
print dir(result[0])

#Access all its attributes
print result[0].name

"""
If you already have the access token for this user
you can go until lines  1- 13, and then get at
your database the access token for this user and
set the access token.

auth.set_access_token('ACCESS_TOKEN')

Now you can go on by the line 33.

"""
