#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Demo Script."""


class AnotherDemo:
    """Another Demo."""

    sex: bool = True

    name: str = "Hello"
    age : int = 30

    @property
    def gender(self) -> str:
        """Get Gender."""
        return "Male" if self.sex else "Female"

    def print_gender(self) -> str:
        """Print Gender."""
        print(self.gender)
        return self.gender



class TestAnotherDemo:
    """Test Another Demo."""

    app = AnotherDemo()

    def run_test(self) -> None:
        """Run Test."""
        raise NotImplementedError

    def run(self) -> None:
        """Run."""
        print(self.app.gender)
        self.app.print_gender()

        self.app.sex = False
        print(self.app.gender)
        self.app.print_gender()


if __name__ == "__main__":
    TestAnotherDemo().run()
