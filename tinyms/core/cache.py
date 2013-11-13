__author__ = 'tinyms'

import os
import tempfile
from hashlib import md5
from time import time

try:
    import cPickle as pickle
except ImportError:  # pragma: no cover
    import pickle

class CacheManager(object):
    __disk_path__ = ""
    @staticmethod
    def get(threshold=500, default_timeout=300):
        if not CacheManager.__disk_path__:
            return SimpleCache(threshold,default_timeout)
        return FileSystemCache(threshold,default_timeout)

class BaseCache(object):
    """Baseclass for the cache systems.  All the cache systems implement this
    API or a superset of it.

    :param default_timeout: the default timeout that is used if no timeout is
                            specified on :meth:`set`.
    """

    def __init__(self, default_timeout=300):
        self.default_timeout = default_timeout

    def get(self, key):
        """Looks up key in the cache and returns the value for it.  If the key
        does not exist or is unreadable `None` is returned instead.

        :param key: the key to be looked up.
        """
        return None

    def delete(self, key):
        """Deletes `key` from the cache.  If it does not exist in the cache
        nothing happens.

        :param key: the key to delete.
        :returns: If the key has been deleted.
        """
        return True

    def del_group(self,key_prefix):

        """
        key is '/group/key' or 'group.key' etc.
        key_prefix is '/group' or group
        :param key_prefix:
        :return:
        """
        return True

    def set(self, key, value, timeout=None):
        """Adds a new key/value to the cache (overwrites value, if key already
        exists in the cache).

        :param key: the key to set
        :param value: the value for the key
        :param timeout: the cache timeout for the key (if not specified,
                        it uses the default timeout).
        :returns: ``True`` if key has been updated, ``False`` for backend
                  errors. Pickling errors, however, will raise a subclass of
                  ``pickle.PickleError``.
        """
        return True

    def add(self, key, value, timeout=None):
        """Works like :meth:`set` but does not overwrite the values of already
        existing keys.

        :param key: the key to set
        :param value: the value for the key
        :param timeout: the cache timeout for the key or the default
                        timeout if not specified.
        :returns: Same as :meth:`set`, but also returns `False` for already
                  existing keys.
        :rtype: boolean
        """
        return True

    def clear(self):
        """Clears the cache.  Keep in mind that not all caches support
        completely clearing the cache.
        :returns: If the cache has been cleared.
        :rtype: boolean
        """
        return True


class NullCache(BaseCache):
    """A cache that doesn't cache.  This can be useful for unit testing.

    :param default_timeout: a dummy parameter that is ignored but exists
                            for API compatibility with other caches.
    """


class SimpleCache(BaseCache):
    def __init__(self, threshold=500, default_timeout=300):
        BaseCache.__init__(self, default_timeout)
        self._cache = {}
        self.clear = self._cache.clear
        self._threshold = threshold

    def _prune(self):
        if len(self._cache) > self._threshold:
            now = time()
            for idx, (key, (expires, _)) in enumerate(self._cache.items()):
                if expires <= now or idx % 3 == 0:
                    self._cache.pop(key, None)

    def get(self, key):
        try:
            expires, value = self._cache[key]
            if expires > time():
                return pickle.loads(value)
        except (KeyError, pickle.PickleError):
            return None

    def set(self, key, value, timeout=None):
        if timeout is None:
            timeout = self.default_timeout
        self._prune()
        self._cache[key] = (time() + timeout, pickle.dumps(value,
                                                           pickle.HIGHEST_PROTOCOL))
        return True

    def add(self, key, value, timeout=None):
        if timeout is None:
            timeout = self.default_timeout
        if len(self._cache) > self._threshold:
            self._prune()
        item = (time() + timeout, pickle.dumps(value,
                                               pickle.HIGHEST_PROTOCOL))
        if key in self._cache:
            return False
        self._cache.setdefault(key, item)
        return True

    def delete(self, key):
        return self._cache.pop(key, None) is not None

    def del_group(self,key_prefix):
        keys = set()
        for k in self._cache:
            if k.startswith(key_prefix):
                keys.add(k)
        for key in keys:
            self.delete(key)
        return True

class FileSystemCache(BaseCache):
    #: used for temporary files by the FileSystemCache
    _fs_transaction_suffix = '.__archivex_cache'
    _groups = {}
    def __init__(self, cache_dir, threshold=500, default_timeout=300, mode=0o600):
        BaseCache.__init__(self, default_timeout)
        self._path = cache_dir
        self._threshold = threshold
        self._mode = mode
        if not os.path.exists(self._path):
            os.makedirs(self._path)

    def _list_files(self):
        """
        return a list of (fully qualified) cache filenames
        """
        return [os.path.join(self._path, fn) for fn in os.listdir(self._path) if not fn.endswith(self._fs_transaction_suffix)]

    def _prune(self):
        entries = self._list_files()
        if len(entries) > self._threshold:
            now = time()
            try:
                for idx, fname in enumerate(entries):
                    with open(fname, 'rb') as f:
                        expires = pickle.load(f)
                    remove = expires <= now or idx % 3 == 0
                    if remove:
                        os.remove(fname)
            except (IOError, OSError):
                pass

    def clear(self):
        self._groups.clear()
        for fname in self._list_files():
            try:
                os.remove(fname)
            except (IOError, OSError):
                return False
        return True

    def _get_filefullname(self, key):
        fn = self._groups.get(key)
        if fn:
            return fn
        else:
            hash = md5(key.encode('utf-8')).hexdigest()
            fullpath = os.path.join(self._path, hash)
            self._groups[key] = fullpath
            return fullpath

    def get(self, key):
        filename = self._get_filefullname(key)
        try:
            with open(filename, 'rb') as f:
                if pickle.load(f) >= time():
                    return pickle.load(f)
                else:
                    os.remove(filename)
                    return None
        except (IOError, OSError, pickle.PickleError):
            return None

    def add(self, key, value, timeout=None):
        filename = self._get_filefullname(key)
        if not os.path.exists(filename):
            return self.set(key, value, timeout)
        return False

    def set(self, key, value, timeout=None):
        if timeout is None:
            timeout = self.default_timeout
        filename = self._get_filefullname(key)
        self._prune()
        try:
            fd, tmp = tempfile.mkstemp(suffix=self._fs_transaction_suffix,
                                       dir=self._path)
            with os.fdopen(fd, 'wb') as f:
                pickle.dump(int(time() + timeout), f, 1)
                pickle.dump(value, f, pickle.HIGHEST_PROTOCOL)
            os.rename(tmp, filename)
            os.chmod(filename, self._mode)
        except (IOError, OSError):
            return False
        else:
            return True

    def delete(self, key):
        try:
            os.remove(self._get_filefullname(key))
        except (IOError, OSError):
            return False
        else:
            return True

    def del_group(self,key_prefix):
        for k in self._groups:
            if k.startswith(key_prefix):
                try:
                    os.remove(self._groups[k])
                except (IOError, OSError):
                    return False
        return True

# c = CacheManager.create()
# c.add("/category/org",[1,2,3,4])
# c.add("/category/roles",(2,3,4,5,6))
# print(c.get("/category/org"),c.get("/category/roles"))
# print(c.del_group("/category"))