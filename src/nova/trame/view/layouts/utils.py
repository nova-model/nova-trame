"""Utilities for our layout components."""

from typing import Dict, Union


def merge_styles(*styles: Union[Dict[str, str], str]) -> str:
    result = ""

    for style in styles:
        if isinstance(style, dict):
            for key, value in style.items():
                result += f" {key}: {value};"
        else:
            result += f" {style};"

    return result
