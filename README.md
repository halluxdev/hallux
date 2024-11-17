# Hallux - Convenient AI Code Quality Assistant

`Hallux` is a smart console utility to help you with routine code quality tasks.
It may help you with fixing SonarQube issues, linting issues, compilation errors and other code quality problems.
Any annoying issue, requiring a bit more intelligence than usual might be tackled.

In order to fix code issues directly in your local filesystem, just type

> hallux .

If you want to fix issues in a orderly manner, where every fix has its own `git commit` run

> hallux --git .

If you want `hallux` to propose you fixes and corrections directly into your Pull-Request, you may add following line into the CI

> hallux --github https://github.com/ORG_NAME/REPO_NAME/pull/ID .

`Hallux` will go to Github Web GUI and will send all its findings as comments with code proposals.

In order for `hallux` to understand your repo you need to provide `.hallux` configuration file, in the repo root folder.  
For more command-line commands and just type `$ hallux`

## Installation

```bash
pip install hallux

hallux
```

## Local development

In order to setup Python virtual environment run `./scripts/setup-venv.sh`

For activating environment run `source ./activate.sh`

## Folder structure

- **bin** main hallux executable
- **hallux** main source codes for hallux
- **scripts** complimentary scripts for managing the repo
- **tests** unit- and integration- tests for hallux

test
