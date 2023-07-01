#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Reddit Helpers."""

from time import sleep
from random import choice, uniform

import regex as re
from requests import Session

from ..base.io import IO
from ..base.imap import ImapClient
from ..base.proxy import Proxy

from ..config import Config
from ..utils import Utils


class RedditHelpers:
    """Reddit Helpers."""

    config = Config()
    utils = Utils()

    debug = True
    timeout = 30

    def __init__(self) -> None:
        "Init Reddit Helper."
        self.list_ua = self.load_ua()
        self.list_px = self.load_proxy()
        assert self.list_ua
        assert self.list_px

    def load_ua(self) -> list[str]:
        """Load list of User-Ageng string."""
        file_ua = self.config.dir_dat / "ua.txt"
        return IO.load_line(file_name=file_ua, keyword="Mozilla")

    def load_proxy(self) -> list[str]:
        """Load list of proxy string."""
        file_proxy = self.config.dir_dat / "proxy.txt"
        return IO.load_line(file_name=file_proxy, keyword="http")

    def new_browser(self) -> Session:
        """Generate New Random requests.Session as Browser."""
        ua = choice(self.list_ua)
        px = choice(self.list_px)
        br = Session()
        br.headers.update({"User-Agent": ua})
        br.proxies = {
            "http": px,
            "https": px
        }
        return br

    @staticmethod
    def delay(a: float, b: float) -> float:
        """Delay for random seconds in (a, b)."""
        num = uniform(a, b)
        sleep(num)
        return num

    def http_get_json(self, url: str, retry: int = 3) -> dict:
        """Http GET Method to get json response."""
        br = self.new_browser()
        for _ in range(retry):
            try:
                with br.get(url=url, timeout=self.timeout) as res:
                    if res:
                        return res.json()
            except Exception as e:
                if self.debug:
                    raise Exception(e)
            self.delay(1, 3)
        return {}
                
    def http_get_html(self, url: str, retry: int = 3) -> str:
        """Http GET Method to get html response."""
        br = self.new_browser()
        for _ in range(retry):
            try:
                with br.get(url=url, timeout=self.timeout) as res:
                    if res:
                        return res.text
            except Exception as e:
                if self.debug:
                    raise Exception(e)
            self.delay(1, 3)
        return ""

    def get_verify_url_mail_ru(self, email_user: str, email_pass: str, proxy_url: str, timestamp: int = 0) -> list[str]:
        """Get Reddit verify url from mail.ru inbox."""
        query = ""
        pattern = re.compile(r"")

        proxy = Proxy.load(url=proxy_url)
        im = ImapClient(
            host="imap.yandex.com",
            port=993,
            usr=email_user,
            pwd=email_pass,
            ssl_enable=True,
            proxy=proxy,
        )
        return im.lookup(query=query, pattern=pattern, timestamp=timestamp)

    def is_alive_user(self, name: str) -> bool:
        """Check if redditor alive."""
        url = f"https://www.reddit.com/user/{name}/about.json"
        about = self.http_get_json(url)
        data = about["data"]
        return not "is_suspended" in data