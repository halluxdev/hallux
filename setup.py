from __future__ import annotations

import os
import pathlib

from setuptools import setup

here = pathlib.Path(__file__).parent.resolve()


def get_version() -> str:
    # check auto-genertated file for latest version
    version_py = here / "bin/__version__.py"
    if version_py.exists():
        with open(version_py) as fp:
            for line in fp.read().splitlines():
                if line.startswith("version"):
                    delim = '"' if '"' in line else "'"
                    return line.split(delim)[1]

    # check env variable
    version_env: str | None = os.environ.get("HALLUX_VERSION", None)
    if version_env is not None:
        return version_env

    return "DEVELOP"


# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="hallux",
    version=get_version(),
    description="Convenient Coding Assistant.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/halluxdev/hallux",
    project_urls={
        "Documentation": "https://hallux.dev/doc",
    },
    author="Hallux.Dev Team",
    author_email="sergey@hallux.dev",
    license="PRIVARE",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    package_dir={"": "bin"},
    install_requires=["ruff", "mypy", "openai", "pyyaml", "PyGithub"],
    entry_points={
        "console_scripts": [
            "hallux=hallux:main",
        ],
    },
    zip_safe=False,
    python_requires=">=3.7",
)
