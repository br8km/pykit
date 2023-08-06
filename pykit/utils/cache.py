#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""File Caches & Memory Caches.

Features:
- File Cache
- Memory Cache
- Bulk Operation
- Thread safe
- Iterable prefer?

"""

from time import time, sleep
from pathlib import Path
from threading import RLock, Thread
from typing import KeysView, ValuesView, ItemsView, Optional

from ..base.io import IO
from ..config import Config


__all__ = ("FileCache", "MemoryCache", )


GLOBAL_LOCK = RLock()  # for threqd safe


class AbsCache:
    """Cache."""

    key_cache = "cache_time"

    @staticmethod
    def now() -> int:
        """Get utcnow timestamp."""
        return int(time())

    @classmethod
    def ts_expire(cls, seconds: int) -> int:
        """Get expected timestamp to be expired."""
        assert seconds >= 0
        return cls.now - seconds

    @classmethod
    def is_expired(cls, item: dict, seconds: int) -> bool:
        """Check if item expired or not."""
        expired = cls.ts_expire(seconds=seconds)
        return item[cls.key_cache] <= expired


class FileCache(AbsCache):
    """File Cache. 

    Notes:
        - If need frequent Operation, Please Use Memory Cache.
    
    """

    # --- cache for Any data

    @classmethod
    def has_file(cls, file: Path, seconds: int) -> bool:
        """Has cached file for seconds or Not."""
        with GLOBAL_LOCK:
            expired = cls.ts_expire(seconds=seconds)
            return bool(
                file.is_file()
                and file.stat().st_mtime > expired
            )

    @classmethod
    def prune_file(cls, file: Path, seconds: int) -> None:
        """Prune cache file expired out of seconds."""
        with GLOBAL_LOCK:
            expired = cls.ts_expire(seconds=seconds)
            if file.is_file() and file.stat().st_mtime <= expired:
                file.unlink()

    @classmethod
    def prune_dir(cls, dir: Path, seconds: int) -> None:
        """Prune cache files from dir which expired out of seconds."""
        with GLOBAL_LOCK:
            expired = cls.ts_expire(seconds=seconds)
            for fp in dir.iterdir():
                if fp.is_file() and fp.stat().st_mtime <= expired:
                    fp.unlink()

    # --- cache for list of dict

    @classmethod
    def prune_list_dict(cls, data: list[dict], seconds: int) -> list[dict]:
        """Prune list of dict."""
        expired = cls.ts_expire(seconds=seconds)
        return [item for item in data if item[cls.key_cache] > expired]

    @classmethod
    def load_list_dict(cls, file: Path, seconds: int) -> list[dict]:
        """Load list of user dict from local cache."""
        with GLOBAL_LOCK:
            result: list[dict] = []
            if file.is_file():
                data = IO.load_list_dict(file)
                return cls.prune_list_dict(data=data, seconds=seconds)
            return result

    @classmethod
    def add_list_dict(cls, file: Path, item: dict, seconds: int) -> bool:
        """Add one item into local cache."""
        with GLOBAL_LOCK:
            cached = cls.load_list_dict(file=file, seconds=seconds)
            item[cls.key_cache] = cls.now()
            cached.append(item)
            IO.save_list_dict(file_name=file, file_data=cached)
            return file.is_file()

    @classmethod
    def add_list_dict_many(cls, file: Path, data: list[dict], seconds: int) -> bool:
        """Save list of items into local cache."""
        with GLOBAL_LOCK:
            cached = cls.load_list_dict(file=file, seconds=seconds)
            for item in data:
                item[cls.key_cache] = cls.now()
                cached.append(item)
            IO.save_list_dict(file_name=file, file_data=cached)
            return file.is_file()

    # --- cache for dict of dict

    @classmethod
    def prune_dict_dict(cls, data: dict[str, dict], seconds: int) -> dict[str, dict]:
        """Prune dict of dict."""
        expired = cls.ts_expire(seconds=seconds)
        return {key: item for key, item in data if item[cls.key_cache] > expired}

    @classmethod
    def load_dict_dict(cls, file: Path, seconds: int) -> dict[str, dict]:
        """Load dict of dict from local cache."""
        with GLOBAL_LOCK:
            result: dict[str, dict] = {}
            if file.is_file():
                data = IO.load_dict(file)
                return cls.prune_dict_dict(data=data, seconds=seconds)
            return result

    @classmethod
    def add_dict_dict(cls, file: Path, key: str, value: dict, seconds: int) -> bool:
        """Add one key:item into local cache."""
        with GLOBAL_LOCK:
            cached = cls.load_dict_dict(file=file, seconds=seconds)
            value[cls.key_cache] = cls.now()
            cached[key] = value
            IO.save_dict(file_name=file, file_data=cached)
            return file.is_file()

    @classmethod
    def add_dict_dict_many(cls, file: Path, data: dict[str, dict], seconds: int) -> bool:
        """Add one key:item into local cache."""
        with GLOBAL_LOCK:
            cached = cls.load_dict_dict(file=file, seconds=seconds)
            for key, item in data.items():
                item[cls.key_cache] = cls.now()
                cached[key] = item
            IO.save_dict(file_name=file, file_data=cached)
            return file.is_file()


class MemoryCache(AbsCache):
    """Memory Cache."""

    _file: Path
    _seconds: int
    _lock: RLock
    _cache: dict[str, dict]

    def __init__(self, 
                 file: Path,
                 seconds: int = 86400 * 7,
                 lock: Optional[RLock] = None) -> None:

        """Init."""
        self._file = file
        self._seconds = seconds
        self._lock = lock if lock else RLock()
        self._cache = {}

        self.load(file=file)

    def load(self) -> bool:
        """Load cache data from File."""
        with self._lock:
            if self._file.is_file():
                self._cache = IO.load_dict(self._file)
                self.prune()
            return bool(self._cache)
                
    def save(self) -> bool:
        """Save cache data into File."""
        with self._lock:
            self.prune()
            if self._cache:
                IO.save_dict(file_data=self._file, file_data=self._cache)
                return self._file.is_file()
            else:
                self._file.unlink(missing_ok=True)
                return not self._file.is_file()

    def prune(self) -> int:
        """Prune any expired items from cache.

        Returns:
            number of pruned items which expired as of now.
        
        """
        count = 0
        for key, value in self.items():
            if self.is_expired(item=value, seconds=self._seconds):
                count += self.delete(key)
        return count

    def exit(self) -> None:
        """Exit."""
        self.prune()
        self.save(file=self._file)

    def set(self, key: str, value: dict) -> None:
        """Set key:value for cache."""
        value[self.key_cache] = self.now()
        self._cache[key] = value

    def set_many(self, items: dict[str, dict]) -> None:
        """Set many key:value for cache."""
        for key, value in items.items():
            self.set(key=key, value=value)

    def add(self, key: str, value: dict, force: bool = False) -> None:
        """Add key:value into cache, set force to update if exist."""
        if self.has(key) and not force:
            return
        self.set(key=key, value=value)

    def add_many(self, items: dict[str, dict], force: bool = False) -> None:
        """Add many key:value into cache, set force to update if exist."""
        for key, value in items.items():
            self.add(key=key, value=value, force=force)

    def delete(self, key: str) -> int:
        """Delete item for cache by key string."""
        count = 0
        try:
            del self._cache[key]
            count += 1
        except KeyError:
            pass
        return count

    def delete_many(self, keys: list[str]) -> int:
        """Delete many items from cache by keys."""
        count = 0
        for key in keys:
            count += self.delete(key)
        return count

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
        return self._cache.keys()

    def values(self) -> ValuesView:
        """
        Return ``dict_values`` view of all cache values.

        Note:
            Cache is copied from the underlying cache storage before returning.
        """
        return self._cache.values()

    def items(self) -> ItemsView:
        """
        Return a ``dict_items`` view of cache items.

        Warning:
            Returned data is copied from the cache object, but any modifications to mutable values
            will modify this cache object's data.
        """
        return self._cache.items()

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()

    def has(self, key: str) -> bool:
        """Return whether cache key exists and hasn't expired."""
        with self._lock:
            value = self.get(key=key)
            return bool(value)

    def size(self) -> int:
        """Return number of cache entries."""
        return len(self._cache)

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
            try:
                value = self._cache.get(key, {})
                if value:
                    if self.is_expired(item=value, seconds=self._seconds):
                        self.delete(key)
                        raise KeyError
            except KeyError:
                value = {}
            return value


class TestCache:
    """Test Cache."""

    config = Config()

    dir_cache = config.dir_debug / "testcache"
    dir_cache.mkdir(parents=True, exist_ok=True)
    file_cache = dir_cache / "cache.json"

    def test_abscache(self, seconds: int = 5) -> None:
        """Test AbsCache."""
        app = AbsCache()

        assert app.now <= int(time())

        item: dict[str, int] = {
            "name": "item_name",
            app.key_cache: app.ts_expire(seconds=seconds)
        }
        assert not app.is_expired(item=item, seconds=seconds)
        sleep(secs=seconds + 1)
        assert app.is_expired(item=item, seconds=seconds)

    def test_filecache(self, seconds: int = 5) -> None:
        """Test FileCache."""
        app = FileCache()

        # test filecache for any data
        assert not app.has_file(file=self.file_cache, seconds=seconds)

        # save file for string content
        IO.save_str(file_name=self.file_cache, file_content="hello")
        assert app.has_file(file=self.file_cache, seconds=seconds)

        # prune file
        app.prune_file(file=self.file_cache, seconds=seconds)
        # still exist
        assert app.has_file(file=self.file_cache, seconds=seconds)
        # wait for seconds + 1
        sleep(secs=seconds + 1)
        # file been pruned
        assert not app.has_file(file=self.file_cache, seconds=seconds)

        # save file for bytes content
        IO.save_bytes(file_name=self.file_cache, file_content=b"hello")
        assert app.has_file(file=self.file_cache, seconds=seconds)
        sleep(secs=seconds + 1)
        # wait for seconds + 1 and prune dir
        app.prune_dir(dir=self.dir_cache)
        # dir|file been pruned
        assert not app.has_file(file=self.file_cache, seconds=seconds)

        # cache operate for list of dict items
        items_ld: list[dict] = [{"age": age} for age in range(5)]

        # start with no cache
        self.file_cache.unlink(missing_ok=True)
        result_ld = app.load_list_dict(file=self.file_cache, seconds=seconds)
        assert len(result_ld) == 0

        # add one item into cache
        app.add_list_dict(
            file=self.file_cache,
            item=items_ld[0],
            seconds=seconds,
        )
        result_ld = app.load_list_dict(file=self.file_cache, seconds=seconds)
        assert len(result_ld) == 1

        # add remain items into cache
        app.add_list_dict_many(
            file=self.file_cache,
            data=items_ld[1:],
            seconds=seconds,
        )
        # wait half of seconds defined before
        sleep(seconds / 2)
        result_ld = app.load_list_dict(file=self.file_cache, seconds=seconds)
        assert len(result_ld) == len(items_ld)

        # wait another half of seconds defined before plus 1
        sleep(seconds / 2 + 1)
        result_ld = app.load_list_dict(file=self.file_cache, seconds=seconds)
        assert len(result_ld) == 0

        # cache operate for dict of dict items
        items_dd: dict[str, dict] = {f"idx_{i}": {"idx": i} for i in range(5)}

        # start with no cache
        self.file_cache.unlink(missing_ok=True)
        result_dd = app.load_dict_dict(file=self.file_cache, seconds=seconds)
        assert len(result_dd) == 0

        # add one key:value into cache
        key_0 = items_dd.keys()[0]
        value_0 = items_dd[key_0]
        app.add_dict_dict(
            file=self.file_cache,
            key=key_0,
            value=value_0,
            seconds=seconds,
        )
        result_dd = app.load_dict_dict(file=self.file_cache, seconds=seconds)
        assert len(result_dd) == 1

        # add remain items into cache
        key_0 = items_dd.keys()[0]
        remain = {k:v for k, v in items_dd if k!=key_0}
        app.add_list_dict_many(
            file=self.file_cache,
            data=remain,
            seconds=seconds,
        )
        # wait half of seconds defined before
        sleep(seconds / 2)
        result_dd = app.load_dict_dict(file=self.file_cache, seconds=seconds)
        assert len(result_dd) == len(items_dd)

        # wait another half of seconds defined before plus 1
        sleep(seconds / 2 + 1)
        result_dd = app.load_dict_dict(file=self.file_cache, seconds=seconds)
        assert len(result_dd) == 0

        # clean up cache file|dir
        self.file_cache.unlink(missing_ok=True)
        self.dir_cache.rmdir()

    def _test_memorycache(self) -> None:
        """Test MemoryCache."""
        raise NotImplementedError

    def test_memorycache(self, lock: RLock, seconds: int = 5) -> None:
        """Test MemoryCache."""
        items_dd: dict[str, dict] = {f"idx_{i}": {"idx": i} for i in range(5)}

        # start with no cached item
        app = MemoryCache(file=self.file_cache, seconds=seconds, lock=lock)
        assert app.size() == 0

        # add one key:value into cache
        key_0 = items_dd.keys()[0]
        value_0 = items_dd[key_0]
        app.add(
            key=key_0,
            value=value_0,
            force=False,
        )
        assert app.size() == 1

        # add remain items into cache
        key_0 = items_dd.keys()[0]
        remain = {k:v for k, v in items_dd if k!=key_0}
        app.add_many(
            items=remain,
            force=False,
        )
        # wait half of seconds defined before
        sleep(seconds / 2)
        assert app.size() == len(items_dd)

        # wait another half of seconds defined before plus 1
        sleep(seconds / 2 + 1)
        assert app.size() == 0

        # add all items again
        app.add_many(items=items_dd)
        assert app.size() == len(items_dd)

        # delete first key:value
        key_0 = items_dd.keys()[0]
        app.delete(key=key_0)
        assert app.size() == len(items_dd) - 1

        # delete another two key:value
        keys_2 = items_dd.keys()[1:2]
        app.delete_many(keys=keys_2)
        assert app.size() == len(items_dd) - 3

        # save remain items into file
        assert app.save()

        # clear all items
        app.clear()
        assert app.size() == 0
        assert app.save()

        # clean up cache file|dir
        self.file_cache.unlink(missing_ok=True)
        self.dir_cache.rmdir()

    def test_memorycache_multi(self, num: int = 2, seconds: int = 5) -> None:
        """Test MemoryCache in multi-threading."""
        lock = RLock()
        threads: list[Thread] = []
        for _ in range(num):
            th = Thread(target=self.test_memorycache, args=(lock, seconds,))
            threads.append(th)
            th.start()

        for th in threads:
            th.join()

        for th in threads:
            assert not th.is_alive()

    def run_test(self) -> None:
        """Run Test."""
        raise NotImplementedError


if __name__ == "__main__":
    TestCache().run_test()