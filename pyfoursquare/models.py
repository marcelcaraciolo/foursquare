# -*- coding: utf-8 -*-


"""
A Python interface for the Foursquare API.

If you are looking for a complete foursquare-APIv2 reference, go to

    <http://developer.foursquare.com/docs/>


https://github.com/marcelcaraciolo/foursquare


"""


class ResultSet(list):
    """A list like object that holds results from a Twitter API query."""


class Model(object):

    def __init__(self, api=None):
        self._api = api

    def __getstate__(self):
        # pickle
        pickle = dict(self.__dict__)
        try:
            del pickle['_api']  # do not pickle the API reference
        except KeyError:
            pass
        return pickle

    @classmethod
    def parse(cls, api, json):
        """Parse a JSON object into a model instance."""
        raise NotImplementedError

    @classmethod
    def parse_list(cls, api, json_list):
        """Parse a list of JSON objects into a result set of model instances."""
        results = ResultSet()
        for obj in json_list:
            if obj:
                results.append(cls.parse(api, obj))
        return results


class Location(Model):
    @classmethod
    def parse(cls, api, json):
        location = cls(api)
        for k, v in json.items():
            setattr(location, k, v)

        return location


class Contact(Model):
    @classmethod
    def parse(cls, api, json):
        contact = cls(api)
        for k, v in json.items():
            setattr(contact, k, v)

        return contact


class Stats(Model):
    @classmethod
    def parse(cls, api, json):
        stats = cls(api)
        for k, v in json.items():
            setattr(stats, k, v)

        return stats


class Category(Model):
    @classmethod
    def parse(cls, api, json):
        stats = cls(api)
        for k, v in json.items():
            setattr(stats, k, v)

        return stats

    def __repr__(self):
        return self.name


class Venue(Model):
    @classmethod
    def parse(cls, api, json):
        venue = cls(api)
        for key, value in json.items():
            if key == 'location':
                setattr(venue, key, Location.parse(api, value))
            elif key == 'contact':
                setattr(venue, key, Contact.parse(api, value))
            elif key == 'beenHere':
                setattr(venue, key, value['count'])
            elif key == 'stats':
                setattr(venue, key, Stats.parse(api, value))
            elif key == 'tips':
                pass
                #we will use api for this.
            elif key == 'categories':
                setattr(venue, key, Category.parse_list(api, value))
            else:
                setattr(venue, key, value)
        #print venue.listed
        #print venue.hereNow
        #print venue.createdAt
        #print venue.mayor
        #print venue.photos
        #print venue.specials
        return venue

    def tips(self, **kwargs):
        return self._api.venues_tips(id=self.id, **kwargs)

    def __repr__(self):
        return self.name.encode('utf-8')


class User(Model):
    @classmethod
    def parse(cls, api, json):
        user = cls(api)
        for key, value in json.items():
            if key == 'contact':
                setattr(user, key, Contact.parse(api, value))
            elif key == 'homeCity':
                try:
                    city, country = value.split(',')
                    setattr(user, 'country', city)
                except ValueError:
                    city = value.split(',')
                setattr(user, 'city', city)
            else:
                setattr(user, key, value)
        return user

    def __repr__(self):
        return self.name


class Tip(Model):
    @classmethod
    def parse(cls, api, json):
        tip = cls(api)
        for key, value in json.items():
            if key == 'done' or key == 'todo':
                setattr(tip, key, value['count'])
            elif key == 'user':
                setattr(tip, key, User.parse(api, value))

            else:
                setattr(tip, key, value)
        return tip

    def __repr__(self):
        return self.text[:10].encode('utf-8')


class SearchResult(Model):
    @classmethod
    def parse(cls, api, json):
        return Venue.parse(api, json)


class ModelFactory(object):
    """
    Used by parsers for creating instances
    of models. You may subclass this factory
    to add your own extended models.
    """

    venue = Venue
    tips = Tip
    user = User
    venues = SearchResult
