import os
import pathlib
from textwrap import dedent

from invoke import Program as Programme

programme = Programme()


def main():
    if not os.path.exists("tasks.py"):
        print("Not tasks.py found; creating default...")
        name = pathlib.Path.cwd().name
        with open("tasks.py", "w") as f:
            f.write(
                dedent(
                    f"""
                import hedy


                namespace = hedy.app("{name}")
                """
                )
            )
    programme.run()
