from codedown.__main__ import _rewrite_argv_for_implicit_convert


def test_rewrite_leaves_subcommands():
    assert _rewrite_argv_for_implicit_convert(["code-down", "themes"]) == [
        "code-down",
        "themes",
    ]
    assert _rewrite_argv_for_implicit_convert(["code-down", "config"]) == [
        "code-down",
        "config",
    ]


def test_rewrite_inserts_convert_for_file():
    assert _rewrite_argv_for_implicit_convert(["code-down", "file.md"]) == [
        "code-down",
        "convert",
        "file.md",
    ]
    assert _rewrite_argv_for_implicit_convert(["code-down", "file.md", "temp"]) == [
        "code-down",
        "convert",
        "file.md",
        "temp",
    ]


def test_rewrite_inserts_convert_for_watch_flag():
    assert _rewrite_argv_for_implicit_convert(["code-down", "-w", "file.md"]) == [
        "code-down",
        "convert",
        "-w",
        "file.md",
    ]


def test_rewrite_does_not_touch_help_or_version():
    assert _rewrite_argv_for_implicit_convert(["code-down", "-h"]) == [
        "code-down",
        "-h",
    ]
    assert _rewrite_argv_for_implicit_convert(["code-down", "--help"]) == [
        "code-down",
        "--help",
    ]
    assert _rewrite_argv_for_implicit_convert(["code-down", "-v"]) == [
        "code-down",
        "-v",
    ]
    assert _rewrite_argv_for_implicit_convert(["code-down", "--version"]) == [
        "code-down",
        "--version",
    ]
