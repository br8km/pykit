#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Demo Script."""


from pathlib import Path



class AnotherDemo:
    """Another Demo."""



    def run(self) -> None:
        """Run."""
        dir_app = Path(__file__).parent
        file_no = dir_app / "error.txt"
        content = open(file_no, "r").read()


if __name__ == "__main__":
    AnotherDemo().run()
