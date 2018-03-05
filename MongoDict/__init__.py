#!/usr/bin/env python
# Alexander Hirschfeld <alex@d-qoi.com>

"""This module contains the base class for a dictionary backed by MongoDB."""


from pymongo import collection as MDB_collection
from collections import defaultdict

class MongoDict(dict):
    def __init__(self, collection=None, mirror=True, write_back=True, warm_cache=False):
        """

        :param collection: A pointer to the collection to use :: client[database][collection]
        :param mirror: When set to True, it will pull Everything from the collection provided
          and load it into a dictionary, this may make lookups faster as it will not pull from
          the database for every get, it will write through to provide consistency.
          If the database is updated behind the cache, it will not be updated locally
        :param write_back: When set to false, it will not write to the database, if you want a read_only database
        :param warm_cache: When this is true, it will pull everything immediately

        Setting Mirrored true and write_back to false will make this behave like a regular dictionary
        """
        if not isinstance(collection, MDB_collection.Collection):
            raise TypeError("Collection is not pymongo database:: {}".format(collection))
        self.collection = collection
        self.mirror = mirror
        self.write_back = write_back
        self.idb = defaultdict(dict)
        if warm_cache:
            self.update_from_db()

    def update_from_db(self):
        for dic in self.collection.find({}):
            self.idb[dic['_id']] = dic["data"]

    def __getitem__(self, key):
        res = None
        if self.mirror:
            res = self.idb.get(key, None) # if mirror is false, it will always be empty, using get for the None
        if res:
            return res
        res = self.collection.find_one({"_id":key})
        if not res:
            raise KeyError("{} is not a key".format(key))
        if self.mirror:
            self.idb[res['_id']] = res['data'] # update the cache, so that it can pull faster next time.
        return res["data"]

    def __contains__(self, key):
        if self.mirror:
            if self.idb.__contains__(key):
                return True
        res = self.collection.find_one({"_id" : key})
        if res and self.mirror:
            self.idb[res['_id']] = res['data']
        return bool(res)

    # def __get(self, key):
    #     return self.__getitem__(key)

    def __delitem__(self, key):
        res = None
        if self.write_back:
            res = self.collection.delete_one({"_id":key})
        try:
            self.idb.__delitem__(key)
        except KeyError as e:
            pass
        if res and res.delete_count == 0:
            raise KeyError()

    def __setitem__(self, key, value):
        self.idb[key] = value
        if self.write_back:
            self.collection.update_one({"_id":key}, {'$set':{"data":value}}, upsert=True)

    def __missing__(self, key):
        res = False
        if self.mirror:
            res = self.idb.__missing__(key)
        if not res:
            res = self.collection.find_one({'_id':key})
            if res:
                if self.mirror: # update the cache, if needed
                    self.idb[res['_id']] = res['data']
            return False
        return True

    def clear(self):  # real signature unknown; restored from __doc__
        """ D.clear() -> None.  Remove all items from D. """
        self.idb.clear()
        if self.write_back:
            self.collection.delete_many({})

    def copy(self):  # real signature unknown; restored from __doc__
        """ D.copy() -> a shallow copy of D """
        self.update_from_db()
        return self.idb.copy()


    def get(self, k, d=None):  # real signature unknown; restored from __doc__
        """ D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None. """
        if not self.__missing__(k):
            return self.__getitem__(k)
        return d

    def items(self):  # real signature unknown; restored from __doc__
        self.update_from_db()
        return self.idb.items()

    def keys(self):  # real signature unknown; restored from __doc__
        """ D.keys() -> a set-like object providing a view on D's keys """
        self.update_from_db()
        return self.idb.keys()

    def pop(self, k, d=None):  # real signature unknown; restored from __doc__
        """
        D.pop(k[,d]) -> v, remove specified key and return the corresponding value.
        If key is not found, d is returned if given, otherwise KeyError is raised
        """
        if self.write_back:
            res = self.collection.find_one_and_delete({'_id':k})
        else:
            res = self.collection.find_one({'_id':k})

        if (res == None):
            return self.idb.pop(k, d)
        return res


    def setdefault(self, k, d=None):  # real signature unknown; restored from __doc__
        """ D.setdefault(k[,d]) -> D.get(k,d), also set D[k]=d if k not in D """
        if not self.__missing__(k):
            self.__setitem__(k, d)
            return d
        return self.__getitem__(k)

    def update(self, E=None, **F):  # known special case of dict.update
        """
        D.update([E, ]**F) -> None.  Update D from dict/iterable E and F.
        If E is present and has a .keys() method, then does:  for k in E: D[k] = E[k]
        If E is present and lacks a .keys() method, then does:  for k, v in E: D[k] = v
        In either case, this is followed by: for k in F:  D[k] = F[k]
        """
        if E:
            try:
                for k in E.keys():
                    self.__setitem__(k, E[k])
            except AttributeError as e:
                for k, v in E:
                    self.__setitem__(k, v)
        if F:
            for k in F:
                self.__setitem__(k, F[k])


    def values(self):  # real signature unknown; restored from __doc__
        self.update_from_db()
        return self.values()

    # def __getattribute__(self, *args, **kwargs):  # real signature unknown
    #     """ Return getattr(self, name). """
    #     pass


    def __iter__(self, *args, **kwargs):  # real signature unknown
        self.update_from_db()
        return self.idb.__iter__()

    def __len__(self, *args, **kwargs):  # real signature unknown
        self.update_from_db()
        return self.idb.__len__()

    # @staticmethod  # known case of __new__
    # def __new__(*args, **kwargs):  # real signature unknown
    #     return MongoDict(*args, **kwargs)

    def __repr__(self, *args, **kwargs):  # real signature unknown
        self.update_from_db()
        return self.idb.__repr__()

    def __sizeof__(self):  # real signature unknown; restored from __doc__
        self.update_from_db()
        return self.idb.__sizeof__()

    __hash__ = None
