# Copyright: Hallux team, 2024
from __future__ import annotations


def get_language(filename: str) -> tuple[str, str]:
    ext = filename.split(".")[-1]
    language = ext
    comment_str = "//"

    if ext in ["py"]:
        return "python", "#"

    if ext in ["cpp", "hpp", "c", "h"]:
        return "cpp", comment_str

    if ext in ["js", "jsx", "mjs"]:
        return "javascript", comment_str

    if ext in ["ts", "tsx"]:
        return "typescript", comment_str

    if ext in ["java"]:
        return "java", comment_str

    if ext in ["swift"]:
        return "swift", comment_str

    # TODO: shall we default comment_char?
    return language, None
