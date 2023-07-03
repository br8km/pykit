#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Browser for Scraper, etc. HTTP Tasks."""

from random import choice

from requests import RequestException

from ..base.io import IO
from ..base.log import init_logger
from ..base.debug import Debugger
from ..base.http import Http

from ..config import Config
from ..utils.common import Utils


class Browser:
    """Browser with auto generate HTTP client."""

    config = Config()
    utils = Utils()

    logger = init_logger(name="browser")
    debugger = Debugger(path=config.dir_debug, name="browser")

    def __init__(self) -> None:
        """Init Browser."""
        self.list_ua = self.load_user_agent()
        self.list_px = self.load_proxy()
        assert self.list_ua
        assert self.list_px

        # set client default, you may use random ones later.
        self.client: Http = self.new_client(
            user_agent=self.list_ua[0],
            proxy_url=self.list_px[0],
        )

    def load_user_agent(self) -> list[str]:
        """Load list of User-Ageng string."""
        return IO.load_line(
            file_name=self.config.file_user_agent,
            keyword="Mozilla",
        )

    def load_proxy(self) -> list[str]:
        """Load list of proxy string."""
        return IO.load_line(
            file_name=self.config.file_proxy_url,
            keyword="http",
        )

    def new_client(self, user_agent: str, proxy_url: str) -> Http:
        """Generate New HTTP Client."""
        return Http(
            user_agent=user_agent,
            proxy_url=proxy_url,
            logger=self.logger,
            debugger=self.debugger,
            time_out=self.timeout,
        )

    def rnd_client(self) -> Http:
        """Generate Random Http Client."""
        return self.new_client(
            user_agent=choice(self.list_ua),
            proxy_url=choice(self.list_px),
        )

    def http_get_html(self, url: str, debug: bool = False, retry: int = 3) -> str:
        """HTTP GET Method to get html string from url."""
        for _ in range(retry):
            try:
                with self.client.get(url=url, debug=debug) as response:
                    if response:
                        return response.text
            except RequestException as err:
                if debug:
                    raise err
            self.utils.smart_delay(2)
        return ""

    def http_get_json(self, url: str, debug: bool = False, retry: int = 3) -> dict:
        """HTTP GET Method to get json dict from url."""
        for _ in range(retry):
            try:
                with self.client.get(url=url, debug=debug) as response:
                    if response:
                        return response.json()
            except RequestException as err:
                if debug:
                    raise err
            self.utils.smart_delay(2)
        return {}
