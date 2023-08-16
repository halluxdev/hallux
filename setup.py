import pathlib
from setuptools import setup, find_packages

here = pathlib.Path(__file__).parent.resolve()


def get_version(rel_path: str) -> str:
    with open(here / rel_path) as fp:
        for line in fp.read().splitlines():
            if line.startswith("__version__"):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="hallux",
    version=get_version("src/__version__.py"),
    description="Convenient Coding Assistant.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/halluxai/hallux",
    project_urls={
        "Documentation": "https://hallux.dev/doc",
        "Source": "https://github.com/halluxai/hallux",
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
    # packages=find_packages(
    #     where="src",
    #     exclude=["contrib", "docs", "tests*", "tasks"],
    # ),
    install_requires=["ruff", "mypy", "openai", "pyyaml", "PyGithub"],
    entry_points={
        "console_scripts": [
            "hallux=hallux:main",
        ],
    },
    zip_safe=False,
    python_requires=">=3.7",
)
