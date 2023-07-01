#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Config cls for Helpers."""

from pathlib import Path


class Config:
    """Global Config."""

    dir_app = Path(__file__).parent
    dir_dat = dir_app / "data"
    dir_out = dir_app / "out"
    dir_log = dir_out / "log"
    dir_tmp = dir_out / "tmp"
