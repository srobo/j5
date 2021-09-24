"""
Check that the git tag matches the current j5 version.

For use in CD when auto-releasing to PyPI.

Heavily derived from phial: https://github.com/sedders123/phial/blob/develop/setup.py
"""

import os
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parents[1]


def find_version(*file_paths: str) -> str:
    """
    Find the current formatted version of j5.

    :param file_paths: File path to search in.
    :returns: Formatted j5 version.
    :raises RuntimeError: Unable to find version string.
    """
    with BASE_DIR.joinpath(*file_paths).open() as fp:
        version_file = fp.read()

    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        raw_version = version_match.group(1)
        return f"v{raw_version}"
    raise RuntimeError("Unable to find version string.")


def run() -> None:
    """Check the git version matches the j5 version."""
    tag_ref = os.getenv("GITHUB_REF") or "ENV NOT SET"

    tag_match = re.match(r"ref/tags/(.+)", tag_ref)

    if tag_match:
        tag, = tag_match.groups()
    else:
        print(f"Git Ref {tag_ref} did not match expected format!")
        tag = "UNKNOWN"

    VERSION = find_version("j5", "__init__.py")

    if tag != VERSION:
        info = "Git tag: {0} != j5 version: {1}".format(tag, VERSION)
        sys.exit(info)


if __name__ == "__main__":
    run()
