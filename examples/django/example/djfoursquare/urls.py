from django.conf.urls.defaults import *
from djfoursquare.views import *

urlpatterns = patterns('djfoursquare.views',
    url(r'^$', view=main, name='main'),
    url(r'^callback/$', view=callback, name='auth_return'),
    url(r'^logout/$', view=unauth, name='oauth_unauth'),
    url(r'^auth/$', view=auth, name='oauth_auth'),
    url(r'^info/$', view=info, name='info'),
)
