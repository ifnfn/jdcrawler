#! /usr/bin/python3
# -*- coding: utf-8 -*-

import hashlib
import redis

class CachedBase:
    def __init__(self):
        self.expireTime = 60 * 60

    def Clean(self, regular='*'):
        pass

    def Get(self, key):
        pass

    def Set(self, key, value, timeout=None):
        pass

    def GetKey(self, key):
        return key
        #key = hashlib.sha1(key.encode()).hexdigest()
        #return 'album_' + key

class RedisCached(CachedBase):
    def __init__(self):
        super().__init__()
        self.url_cachedb = redis.Redis(host='127.0.0.1', port=6379, db=2)

    def Clean(self, regular='*'):
        pipe = self.url_cachedb.pipeline()
        for key in self.url_cachedb.keys(regular):
            pipe.delete(key)
        pipe.execute()

    def Get(self, key):
        key = self.GetKey(key)
        value = self.url_cachedb.get(key)
        if type(value) == bytes:
            value = value.decode()

        return value

    def Set(self, key, value, timeout=None):
        key = self.GetKey(key)
        self.url_cachedb.set(key, value)
        if timeout == None:
            timeout = self.expireTime
        self.url_cachedb.expire(key, timeout)

    def Keys(self, regular):
        return self.url_cachedb.keys(regular)
