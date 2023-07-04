#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Reddit Helpers."""


import regex as re

from ..client.imap import ImapClient
from ..base.proxy import Proxy

from ..config import Config
from ..utils.common import Utils
from ..utils.browser import Browser


class RedditHelpers:
    """Reddit Helpers."""

    config = Config()
    utils = Utils()
    browser = Browser()

    debug = True
    timeout = 30

    def __init__(self) -> None:
        "Init Reddit Helper."

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
        about = self.browser.http_get_json(url)
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
        # Sad: mail.ru server imap disabled...


if __name__ == "__main__":
    RedditHelpers().run()
