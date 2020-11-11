# -*- coding: utf-8 -*-

# changed from https://github.com/stucchio/Python-LRU-cache

import time
from collections import OrderedDict


def lru_cache_function(max_size=1024, expiration=15 * 60):
    """
    >>> @lru_cache_function(3, 1)
    ... def f(x):
    ...    print("Calling f(" + str(x) + ")")
    ...    return x
    >>> f(3)
    Calling f(3)
    3
    >>> f(3)
    3
    """

    def wrapper(func):
        return LRUCachedFunction(func, LRUCacheDict(max_size, expiration))

    return wrapper


class LRUCacheDict(object):
    """ A dictionary-like object, supporting LRU caching semantics.

    >>> d = LRUCacheDict(max_size=3, expiration=3)
    >>> d['foo'] = 'bar'
    >>> d['foo']
    'bar'
    >>> import time
    >>> time.sleep(4) # 4 seconds > 3 second cache expiry of d
    >>> d['foo']
    Traceback (most recent call last):
        ...
    KeyError: 'foo'
    >>> d['a'] = 'A'
    >>> d['b'] = 'B'
    >>> d['c'] = 'C'
    >>> d['d'] = 'D'
    >>> d['a'] # Should return value error, since we exceeded the max cache size
    Traceback (most recent call last):
        ...
    KeyError: 'a'

    By default, this cache will only expire items whenever you poke it - all methods on
    this class will result in a cleanup. If the thread_clear option is specified, a background
    thread will clean it up every thread_clear_min_check seconds.

    If this class must be used in a multithreaded environment, the option concurrent should be
    set to true. Note that the cache will always be concurrent if a background cleanup thread
    is used.
    """

    def __init__(self, max_size=1024, expiration=15 * 60):
        self.max_size = max_size
        self.expiration = expiration

        self.__values = {}
        self.__expire_times = OrderedDict()
        self.__access_times = OrderedDict()

    def size(self):
        return len(self.__values)

    def clear(self):
        """
        Clears the dict.

        >>> d = LRUCacheDict(max_size=3, expiration=1)
        >>> d['foo'] = 'bar'
        >>> d['foo']
        'bar'
        >>> d.clear()
        >>> d['foo']
        Traceback (most recent call last):
        ...
        KeyError: 'foo'
        """
        self.__values.clear()
        self.__expire_times.clear()
        self.__access_times.clear()

    def __contains__(self, key):
        return key in self.__values

    def has_key(self, key):
        """
        This method should almost NEVER be used. The reason is that between the time
        has_key is called, and the key is accessed, the key might vanish.

        You should ALWAYS use a try: ... except KeyError: ... block.

        >>> d = LRUCacheDict(max_size=3, expiration=1)
        >>> d['foo'] = 'bar'
        >>> d['foo']
        'bar'
        >>> import time
        >>> if d.has_key('foo'):
        ...    time.sleep(2) #Oops, the key 'foo' is gone!
        ...    d['foo']
        Traceback (most recent call last):
        ...
        KeyError: 'foo'
        """
        return key in self

    def __setitem__(self, key, value):
        t = int(time.time())
        self.__delete__(key)
        self.__values[key] = value
        self.__access_times[key] = t
        self.__expire_times[key] = t + self.expiration
        self.cleanup()

    def __getitem__(self, key):
        self.__access_times.pop(key, None)
        self.__access_times[key] = int(time.time())
        self.cleanup()
        return self.__values[key]

    def __delete__(self, key):
        if key in self.__values:
            self.__values.pop(key, None)
            self.__expire_times.pop(key, None)
            self.__access_times.pop(key, None)

    def cleanup(self):
        if self.expiration is None:
            return None

        key_need_deleted = []
        for k, expire_time in self.__expire_times.items():
            if expire_time < int(time.time()):
                key_need_deleted.append(k)
            else:
                break

        for key in key_need_deleted:
            self.__delete__(key)

        # If we have more than self.max_size items, delete the oldest
        key_need_deleted = []
        delete_size = len(self.__values) - self.max_size
        for k in self.__access_times:
            if delete_size > 0:
                key_need_deleted.append(k)
                delete_size -= 1
            else:
                break

        for key in key_need_deleted:
            self.__delete__(key)


class LRUCachedFunction(object):
    """
    A memoized function, backed by an LRU cache.

    >>> def f(x):
    ...    print("Calling f(" + str(x) + ")")
    ...    return x
    >>> f = LRUCachedFunction(f, LRUCacheDict(max_size=3, expiration=3) )
    >>> f(3)
    Calling f(3)
    3
    >>> f(3)
    3
    >>> import time
    >>> time.sleep(4) #Cache should now be empty, since expiration time is 3.
    >>> f(3)
    Calling f(3)
    3
    >>> f(4)
    Calling f(4)
    4
    >>> f(5)
    Calling f(5)
    5
    >>> f(3) #Still in cache, so no print statement. At this point, 4 is the least recently used.
    3
    >>> f(6)
    Calling f(6)
    6
    >>> f(4) #No longer in cache - 4 is the least recently used, and there are at least 3 others items in cache [3,4,5,6].
    Calling f(4)
    4

    """

    def __init__(self, function, cache=None):
        if cache:
            self.cache = cache
        else:
            self.cache = LRUCacheDict()
        self.function = function
        self.__name__ = self.function.__name__

    def __call__(self, *args, **kwargs):
        # In principle a python repr(...) should not return any # characters.
        key = f'{repr((args, kwargs))}#{self.__name__}'
        try:
            return self.cache[key]
        except KeyError:
            value = self.function(*args, **kwargs)
            self.cache[key] = value
            return value


if __name__ == "__main__":
    import doctest

    doctest.testmod()
