#!/usr/bin/env python3

"""
Tool to extract code snippets from the README into separate files.

Code snippets begin with a line starting with "```python" and end at a line
starting with "```".
"""

import argparse
from pathlib import Path


class SnippetWriter:
    """Writes files with sequentially increasing numbers into a directory."""

    def __init__(self, output_path: Path):
        self.output_path = output_path
        self.next_num = 0

    def write(self, contents: str) -> None:
        """Write the next file using the given contents."""
        path = self.output_path / f"snippet{self.next_num:04d}.py"
        with open(path, "w") as file:
            file.write(contents)
        self.next_num += 1


def extract(input_path: Path, snippet_writer: SnippetWriter) -> None:
    """Look for code snippets in input_path and send them to the snippet_writer."""
    current_code_block = None
    unchecked = None
    with open(input_path, "r") as input_file:
        for line in input_file:
            if current_code_block is not None:
                if line.startswith("```"):
                    # end code block
                    if not unchecked:
                        snippet_writer.write(current_code_block)
                    current_code_block = None
                else:
                    # line inside a code block
                    current_code_block += line
            else:
                if line.startswith("```python"):
                    # start code block
                    current_code_block = ""
                    unchecked = "unchecked" in line


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    extract(args.input_file, SnippetWriter(args.output_dir))


if __name__ == "__main__":
    main()
