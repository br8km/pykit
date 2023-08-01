#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Global Config for Toolkit."""


from pathlib import Path


class Config:
    """Global Config."""

    private = True  # Set Private to protect files upload to github

    timezone = "America/New_York"

    dir_app = Path(__file__).parent.parent

    dir_out = dir_app / "out"
    dir_cache = dir_out / "cache"
    dir_debug = dir_out / "debug"
    dir_log = dir_out / "log"
    dir_tmp = dir_out / "tmp"

    @property
    def dir_data(self) -> Path:
        """Get dir_dat Path."""
        dir_data = self.dir_app / "data"
        return dir_data / "private" if self.private else dir_data

    @property
    def file_user_agent(self) -> Path:
        """File User-Agent."""
        return self.dir_data / "ua.txt"

    @property
    def file_proxy_url(self) -> Path:
        """File Proxy Urls."""
        return self.dir_data / "proxy.txt"
