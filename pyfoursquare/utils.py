# -*- coding: utf-8 -*-


"""
A Python interface for the Foursquare API.

If you are looking for a complete foursquare-APIv2 reference, go to

    <http://developer.foursquare.com/docs/>


https://github.com/marcelcaraciolo/foursquare

"""
from time import mktime, localtime
from datetime import datetime


def parse_datetime(t):
    dt = localtime(t)
    return datetime.fromtimestamp(mktime(dt))
