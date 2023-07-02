#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Global Config for Toolkit."""


from pathlib import Path


class Config:
    """Global Config."""

    private = True

    timezone = "America/New_York"

    dir_app = Path(__file__).parent.parent

    dir_out = dir_app / "out"
    dir_cache = dir_out / "cache"
    dir_debug = dir_out / "debug"
    dir_log = dir_out / "log"
    dir_tmp = dir_out / "tmp"

    def __init__(self) -> None:
        """Init Config."""

    @getattr
    def dir_dat(self) -> Path:
        """Get dir_dat Path."""
        if self.private:
            return  self.dir_app / "data_private"
        return self.dir_app / "data"

    def file_ua(self) -> Path:
        """File User-Agent."""
        return self.dir_dat / "ua.txt"

    def file_proxy(self) -> Path:
        """File Proxy Urls."""
        return self.dir_dat / "proxy.txt"
