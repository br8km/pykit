#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Reddit.com User Alive Checker."""


from ...utils.browser import Browser


class Reddit:
    """Reddit Checker."""

    browser = Browser()

    def __init__(self) -> None:
        "Init Reddit Checker."

    def is_alive(self, name: str) -> bool:
        """Check if redditor alive."""
        url = f"https://www.reddit.com/user/{name}/about.json"
        about = self.browser.http_get_json(url)
        data = about["data"]
        return not "is_suspended" in data

    def run(self) -> None:
        """Run."""
        user_name = "amy"
        alive = self.is_alive(name=user_name)
        print(alive)


if __name__ == "__main__":
    Reddit().run()
