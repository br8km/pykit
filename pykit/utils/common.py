#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Global Utils for Toolkit."""

from pathlib import Path
from time import sleep, time
from random import uniform


class Cache:
    """Cache."""

    def has_cache(self, file: Path, seconds: int = 86400) -> bool:
        """Has cached data file for seconds or Not."""
        assert file.is_file()
        point = time() - seconds
        return (
            file.is_file()
            and file.stat().st_mtime > point
        )

    def clear_caches(self, dir: Path, seconds: int = 86400) -> None:
        """Clear cache files from dir within seconds."""
        assert dir.is_dir()
        point = time() - seconds
        for fp in dir.iterdir():
            if fp.is_file() and fp.stat().st_mtime > point:
                fp.unlink()


class Utils:
    """Global Utils."""

    def delay(self, min_seconds: float, max_seconds: float) -> float:
        """Delay for seconds."""
        seconds = uniform(min_seconds, max_seconds)
        sleep(seconds)
        return seconds

    def smart_delay(self, pause: float) -> float:
        """Smart Delay."""
        return self.delay(
            min_seconds=pause / 2,
            max_seconds=pause * 2,
        )
