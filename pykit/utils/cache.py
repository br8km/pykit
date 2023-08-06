#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""File Caches & Memory Caches."""
 

# TODO: Add long presistence file handler for file caches to save cpu usage.

# Cache cls optimize
# - In-Memory option
# - Bulk operation option
# - Thread safe
# - Cache statistics, resource usage, etc.

from time import time
from pathlib import Path
from threading import RLock
from typing import KeysView, ValuesView, ItemsView

from ..base.io import IO


GLOBAL_LOCK = RLock()  # for threqd safe


class AbsCache:
    """Abstract Cache."""

    # key string for cache time to live: `cache_ttl`.
    key_ttl = "cache_ttl"

    @staticmethod
    def timer() -> int:
        """Get utcnow timestamp."""
        return int(time())

    @classmethod
    def _expired(cls, seconds: int = 0) -> int:
        """Get expected timestamp to be expired."""
        assert seconds >= 0
        return cls.timer() - seconds

    @classmethod
    def _ttl(cls, seconds: int = 0) -> int:
        """Get timestamp to live along with."""
        assert seconds >= 0
        return cls.timer() + seconds


class FileCache(AbsCache):
    """File Cache.

        Notes:
            - cost resource very high, using for NOT very frequent cases.
    
    """

    # --- cache for Any data
    @classmethod
    def has_cache(cls, file: Path, seconds: int) -> bool:
        """Has cached file for seconds or Not."""
        with GLOBAL_LOCK:
            expired = cls._expired(seconds=seconds)
            return bool(
                file.is_file()
                and file.stat().st_mtime > expired
            )

    @classmethod
    def prune_cache(cls, file: Path, seconds: int = 0) -> None:
        """Prune cache file expired out of seconds."""
        with GLOBAL_LOCK:
            expired = cls._expired(seconds=seconds)
            if file.is_file() and file.stat().st_mtime <= expired:
                file.unlink()

    @classmethod
    def prune_caches(cls, dir: Path, seconds: int = 0) -> None:
        """Prune cache files from dir which expired out of seconds."""
        with GLOBAL_LOCK:
            expired = cls._expired(seconds=seconds)
            for fp in dir.iterdir():
                if fp.is_file() and fp.stat().st_mtime <= expired:
                    fp.unlink()

    # --- cache for list of dict

    @classmethod
    def prune_list_dict(cls, data: list[dict], seconds: int) -> list[dict]:
        """Prune list of dict."""
        expired = cls._expired(seconds=seconds)
        return [item for item in data if item[cls.key_ttl] >= expired]

    @classmethod
    def load_list_dict(cls, file: Path, seconds: int) -> list[dict]:
        """Load list of user dict from local cache."""
        with GLOBAL_LOCK:
            if file.is_file():
                data = IO.load_list_dict(file)
                return cls.prune_list_dict(data=data, seconds=seconds)
            return []

    @classmethod
    def add_list_dict(cls, file: Path, item: dict, seconds: int) -> bool:
        """Add one item into local cache."""
        with GLOBAL_LOCK:
            cached = cls.load_list_dict(file=file, seconds=seconds)
            item[cls.key_ttl] = cls._ttl(seconds=seconds)
            cached.append(item)
            IO.save_list_dict(file_name=file, file_data=cached)
            return file.is_file()

    @classmethod
    def save_list_dict(cls, file: Path, data: list[dict], seconds: int) -> bool:
        """Save list of items into local cache."""
        with GLOBAL_LOCK:
            cached = cls.load_list_dict(file=file, seconds=seconds)
            for item in data:
                item[cls.key_ttl] = cls._ttl(seconds=seconds)
                cached.append(item)
            IO.save_list_dict(file_name=file, file_data=cached)
            return file.is_file()

    # --- cache for dict of dict

    @classmethod
    def prune_dict_dict(cls, data: dict[str, dict], seconds: int) -> dict[str, dict]:
        """Prune dict of dict."""
        expired = cls._expired(seconds=seconds)
        return {key: item for key, item in data if item[cls.key_ttl] >= expired}

    @classmethod
    def load_dict_dict(cls, file: Path, seconds: int) -> dict[str, dict]:
        """Load dict of dict from local cache."""
        with GLOBAL_LOCK:
            if file.is_file():
                data = IO.load_dict(file)
                return cls.prune_dict_dict(data=data, seconds=seconds)
            return {}

    @classmethod
    def add_dict_dict(cls, file: Path, key: str, item: dict, seconds: int) -> bool:
        """Add one key:item into local cache."""
        with GLOBAL_LOCK:
            cached = cls.load_dict_dict(file=file, seconds=seconds)
            item[cls.key_ttl] = cls._ttl(seconds=seconds)
            cached[key] = item
            IO.save_dict(file_name=file, file_data=cached)
            return file.is_file()

    @classmethod
    def save_dict_dict(cls, file: Path, data: dict[str, dict], seconds: int) -> bool:
        """Add one key:item into local cache."""
        with GLOBAL_LOCK:
            cached = cls.load_dict_dict(file=file, seconds=seconds)
            for key, item in data.items():
                item[cls.key_ttl] = cls._ttl(seconds=seconds)
                cached[key] = item
            IO.save_dict(file_name=file, file_data=cached)
            return file.is_file()


class MemoryCache(AbsCache):
    """Memory Cache."""

    _cache: dict[str, dict]  # cached data: {key[str]: value[dict]}
    _lock: RLock
    _seconds: int

    def __init__(self, seconds: int = 86400 * 7) -> None:
        """Init."""
        self._cache = {}
        self._lock = RLock()
        self._seconds = seconds

    def load(self, file: Path) -> bool:
        """Load cache data from File."""
        with self._lock:
            if file.is_file():
                self._cache = IO.load_dict(file)
                self.prune()
            return bool(self._cache)
                
    def save(self, file: Path) -> bool:
        """Save cache data into File."""
        with self._lock:
            self.prune()
            if self._cache:
                IO.save_dict(file_data=file, file_data=self._cache)
            return file.is_file()

    def __len__(self) -> int:
        with self._lock:
            return len(self._cache)

    def __contains__(self, key: str) -> bool:
        return self.has(key)

    def copy(self) -> dict[str, dict]:
        """Return a copy of the cache."""
        with self._lock:
            return self._cache.copy()

    def keys(self) -> KeysView:
        """
        Return ``dict_keys`` view of all cache keys.

        Note:
            Cache is copied from the underlying cache storage before returning.
        """
        return self.copy().keys()

    def values(self) -> ValuesView:
        """
        Return ``dict_values`` view of all cache values.

        Note:
            Cache is copied from the underlying cache storage before returning.
        """
        return self.copy().values()

    def items(self) -> ItemsView:
        """
        Return a ``dict_items`` view of cache items.

        Warning:
            Returned data is copied from the cache object, but any modifications to mutable values
            will modify this cache object's data.
        """
        return self.copy().items()

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()

    def has(self, key: str) -> bool:
        """Return whether cache key exists and hasn't expired."""
        with self._lock:
            return key in self.keys()

    def size(self) -> int:
        """Return number of cache entries."""
        return len(self)

    def get(self, key: str) -> dict:
        """
        Return the cache value for `key` or `default` or ``missing(key)`` if it doesn't exist or has
        expired.

        Args:
            key: Cache key.

        Returns:
            The cached value.
        """
        with self._lock:
            return self._get(key)

    def _get(self, key: str) -> dict:
        try:
            value = self._cache[key]
            if self.expired(key):
                self._delete(key)
                raise KeyError
        except KeyError:
            value = {}
        return value

    def add(self, key: str, value: dict, seconds: int = 0) -> None:
        """
        Add cache key/value if it doesn't already exist.

        This method ignores keys that exist which leaves the original seconds in tact.

        Args:
            key: Cache key to add.
            value: Cache value.
            seconds: TTL value. Defaults to ``0``
                by :attr:`timer`.
        """
        with self._lock:
            self._add(key, value, seconds=seconds)

    def _add(self, key: str, value: dict, seconds: int = 0) -> None:
        if self._has(key):
            return
        self._set(key, value, seconds=seconds)

    def add_many(self, items: dict[str, dict], seconds: int = 0) -> None:
        """
        Add multiple cache keys at once.

        Args:
            items: Mapping of cache key/values to set.
            seconds: TTL value. Defaults to ``None`` which uses :attr:`ttl`. Time units are determined
                by :attr:`timer`.
        """
        for key, value in items.items():
            self.add(key, value, seconds=seconds)

    def set(self, key: str, value: dict, seconds: int = 0) -> None:
        """
        Set cache key/value and replace any previously set cache key.

        If the cache key previously existed, setting it will move it to the end of the cache stack
        which means it would be evicted last.

        Args:
            key: Cache key to set.
            value: Cache value.
            seconds: TTL value. Defaults to ``None`` which uses :attr:`ttl`. Time units are determined
                by :attr:`timer`.
        """
        with self._lock:
            self._set(key, value, seconds=seconds)

    def _set(self, key: str, value: dict, seconds: int = 0) -> None:
        if not seconds:
            seconds = self._ttl

        if key not in self._cache:
            self.prune()

        self._delete(key)
        self._cache[key] = value

        if seconds > 0:
            self._expire[key] = self.timer() + seconds

    def set_many(self, items: dict[str, dict], seconds: int = 0) -> None:
        """
        Set multiple cache keys at once.

        Args:
            items: Mapping of cache key/values to set.
            seconds: TTL value. Defaults to ``None`` which uses :attr:`ttl`. Time units are determined
                by :attr:`timer`.
        """
        with self._lock:
            self._set_many(items, seconds=seconds)

    def _set_many(self, items: dict[str, dict], seconds: int = 0) -> None:
        for key, value in items.items():
            self._set(key, value, seconds=seconds)

    def delete(self, key: str) -> int:
        """
        Delete cache key and return number of entries deleted (``1`` or ``0``).

        Args:
            key: Cache key to delete.

        Returns:
            int: ``1`` if key was deleted, ``0`` if key didn't exist.
        """
        with self._lock:
            return self._delete(key)

    def _delete(self, key: str) -> int:
        count = 0

        try:
            del self._cache[key]
            count = 1
        except KeyError:
            pass

        try:
            del self._expire[key]
        except KeyError:
            pass

        return count

    def delete_many(self, keys: list[str]) -> int:
        """
        Delete multiple cache keys at once filtered by an `keys`.

        Args:
            keys: list of key string.

        Returns:
            int: Number of cache keys deleted.
        """
        with self._lock:
            return self._delete_many(keys)

    def _delete_many(self, keys: list[str]) -> int:
        count = 0
        with self._lock:
            keys = self._filter_keys(keys)
            for key in keys:
                count += self._delete(key)
        return count

    def delete_expired(self) -> int:
        """
        Delete expired cache keys and return number of entries deleted.

        Returns:
            int: Number of entries deleted.
        """
        with self._lock:
            return self._delete_expired()

    def _delete_expired(self) -> int:
        if not self._expire:
            return 0

        # Use a static expiration time for each key for better consistency as opposed to
        # a newly computed timestamp on each iteration.
        count = 0
        expires_on = self.timer()
        expire_times = self._expire.copy()

        for key, expiration in expire_times.items():
            if expiration <= expires_on:
                count += self._delete(key)
        return count

    def expired(self, key: str, expires_on: int = 0) -> bool:
        """
        Return whether cache key is expired or not.

        Args:
            key: Cache key.
            expires_on: Timestamp of when the key is considered expired. Defaults to ``None`` which
                uses the current value returned from :meth:`timer`.
        """
        if not expires_on:
            expires_on = self.timer()

        try:
            return self._expire[key] <= expires_on
        except KeyError:
            return key not in self._cache

    def expire_times(self) -> dict[str, int]:
        """
        Return cache expirations for seconds keys.

        Returns:
            dict
        """
        with self._lock:
            return self._expire.copy()

    def get_seconds(self, key: str) -> int:
        """
        Return the remaining time to live of a key that has a seconds.

        Args:
            key: Cache key.

        Returns:
            The remaining time to live of `key` or ``0`` if the key doesn't exist or has expired.
        """
        with self._lock:
            if not self._has(key):
                return 0

            expire_time = self._expire.copy().get(key)
            if expire_time is None:
                return 0

            seconds = expire_time - self.timer()
            return seconds

    def prune(self) -> int:
        """
        Perform cache eviction per the cache replacement policy:

        Returns:
            Number of cache entries evicted.
        """
        return self.delete_expired()