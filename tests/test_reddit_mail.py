#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Test Reddit."""

from ..run.reddit import RedditHelpers


class TestReddit:
    """Test Reddit."""

    app = RedditHelpers()

    def test_get_verify_mail_ru(self) -> None:
        """Test get verify url from mail.ru inbox."""
        proxy_str = "107.172.64.163"
        mail_ru_str = "faltatifoot7597@e1.ru:xLg4DlPs6O:ucoyllckhvcfhsfh:460514"

        proxy_url = f"http://bpusr023:bppwd023@{proxy_str}:12345"
        result = mail_ru_str.split(":")
        email_user = result[0]
        email_pass = result[-1]
        verify_urls = self.app.get_verify_url_mail_ru(
            email_user=email_user,
            email_pass=email_pass,
            proxy_url=proxy_url,
        )
        assert verify_urls
        for url in verify_urls:
            print(url)

    def test_is_alive_user(self) -> None:
        """Test check if reddit user alive or not."""
        user_name = "hello"
        result = self.app.is_alive_user(name=user_name)
        print(f"{user_name}.alive = {result}")

    def run_test(self) -> None:
        """Run Test."""
        raise NotImplementedError


if __name__ == "__main__":
    TestReddit().run_test()
