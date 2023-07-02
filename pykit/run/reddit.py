#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Reddit Helpers."""

from time import sleep
from random import choice, uniform

import regex as re
from requests import Session, RequestException

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
        user_agent = choice(self.list_ua)
        proxy = choice(self.list_px)
        browser = Session()
        browser.headers.update({"User-Agent": user_agent})
        browser.proxies = {
            "http": proxy,
            "https": proxy,
        }
        return browser

    @staticmethod
    def delay(min_seconds: float, max_seconds: float) -> float:
        """Delay for random seconds in (a, b)."""
        num = uniform(min_seconds, max_seconds)
        sleep(num)
        return num

    def http_get_json(self, url: str, retry: int = 3) -> dict:
        """Http GET Method to get json response."""
        browser = self.new_browser()
        for _ in range(retry):
            try:
                with browser.get(url=url, timeout=self.timeout) as res:
                    if res:
                        return res.json()
            except RequestException as err:
                if self.debug:
                    raise err
            self.delay(1, 3)
        return {}

    def http_get_html(self, url: str, retry: int = 3) -> str:
        """Http GET Method to get html response."""
        browser = self.new_browser()
        for _ in range(retry):
            try:
                with browser.get(url=url, timeout=self.timeout) as res:
                    if res:
                        return res.text
            except RequestException as err:
                if self.debug:
                    raise err
            self.delay(1, 3)
        return ""

    def get_verify_url_mail_ru(self,
                               email_user: str,
                               email_pass: str,
                               proxy_url: str,
                               time_stamp: int = 0) -> list[str]:
        """Get Reddit verify url from mail.ru inbox."""
        pattern = re.compile(r'"(https://www.reddit.com/verification/[\s\S]+?)"')
        subject = "Verify your Reddit email address"
        from_email = "noreply@reddit.com"
        to_email = email_user

        proxy = Proxy.load(url=proxy_url)
        client = ImapClient(
            host="imap.yandex.com",
            port=993,
            usr=email_user,
            pwd=email_pass,
            ssl_enable=True,
            proxy=proxy,
        )
        return client.search(
            from_email=from_email,
            to_email=to_email,
            subject=subject,
            pattern=pattern,
            time_stamp=time_stamp)

    def is_alive_user(self, name: str) -> bool:
        """Check if redditor alive."""
        url = f"https://www.reddit.com/user/{name}/about.json"
        about = self.http_get_json(url)
        data = about["data"]
        return not "is_suspended" in data

    def run(self) -> None:
        """Run."""
        urls = self.get_verify_url_mail_ru(
            email_user="ecpraceldue5612@e1.ru",
            email_pass="SpyMh8w5GC",
            proxy_url="http://bpusr023:bppwd023@104.206.203.120:12345",
        )
        print(urls)
        # Sad: imap disabled...


if __name__ == "__main__":
    RedditHelpers().run()
