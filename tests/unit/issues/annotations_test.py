import pytest

from hallux.issues.annotations import get_language


@pytest.mark.parametrize(
    "filename, expected_language, expected_comment",
    [
        ("test.py", "python", "#"),
        ("test.c", "cpp", "//"),
        ("test.h", "cpp", "//"),
        ("path/test-test.js", "javascript", "//"),
        ("path/Test.test.ts", "typescript", "//"),
        ("path/Test_test.swift", "swift", "//"),
        ("test.java", "java", "//"),
    ],
)
def test_get_language(filename: str, expected_language: str, expected_comment: str):
    found_value, given_comment = get_language(filename)
    assert expected_language == found_value
    assert expected_comment == given_comment
