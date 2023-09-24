# hallux - Convenient Coding Assistant

`Hallux` is a smart utility to help you with routine coding tasks. 
It may help you with compilation errors (in C/C++), linting or type-check issues (in Python) or even other problems found with SonarQube.
Any annoying issue, requiring a bit more intelligence than usual might be tackled. 

In order to fix coding problems directly in your local filesystem, just type  
> hallux .

If you want to fix issues in a orderly manner, where every fix has its own `git commit` run
> hallux --git .

If you want `hallux` to propose you fixes and corrections directly into your Pull-Request, you may add following line into the CI
> hallux --github https://github.com/ORG_NAME/REPO_NAME/pull/ID .

`Hallux` will go to Github Web GUI and will send all its findings as comments with code proposals.

In order for `hallux` to understand your repo you need to provide `.hallux` configuration file, in the repo root folder.  
For more command-line commands and just type `$ hallux` 

## Folder structure
* **bin** main hallux executable
* **src** main source codes for hallux
* **scripts** complimentary scripts for managing the repo
* **tests** unit- and integration- tests for hallux 

## Installation

In order to setup Python virtual environment run `./scripts/setup-venv.sh`

For activating environment run `cd /path/to/hallux && source activate.sh` 

You might need to add `export PATH="/Path/to/hallux/bin:$PATH"` into your `~/.bashrc` or `~/.zshrc` file.

