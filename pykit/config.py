#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Global Config for Toolkit."""

from pathlib import Path


class Config:
    """Global Config."""

    private = True

    dir_app = Path(__file__).parent.parent

    dir_dat = dir_app / "data"
    dir_dat_private = dir_app / "data_private"

    dir_out = dir_app / "out"
    dir_cache = dir_out / "cache"
    dir_debug = dir_out / "debug"
    dir_log = dir_out / "log"
    dir_tmp = dir_out / "tmp"
