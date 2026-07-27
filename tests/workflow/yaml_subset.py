"""Parse the small mapping-only YAML subset used by agents/openai.yaml."""

from __future__ import annotations

import json
from pathlib import Path


def load_mapping(path: Path) -> dict[str, object]:
    root: dict[str, object] = {}
    stack: list[tuple[int, dict[str, object]]] = [(-1, root)]

    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if indent % 2:
            raise ValueError(f"line {line_number}: indentation must use two spaces")
        key, separator, raw_value = raw_line.strip().partition(":")
        if not separator or not key:
            raise ValueError(f"line {line_number}: expected a mapping entry")
        while stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1]
        if key in parent:
            raise ValueError(f"line {line_number}: duplicate key {key}")
        if not raw_value.strip():
            value: object = {}
        else:
            try:
                value = json.loads(raw_value.strip())
            except json.JSONDecodeError as error:
                raise ValueError(f"line {line_number}: values must be quoted JSON scalars") from error
        parent[key] = value
        if isinstance(value, dict):
            stack.append((indent, value))
    return root
