# hallux - Convenient Coding Assistant

`Hallux` is a smart utility to help you with routine coding tasks. It may help you with compilation errors, linting or type-check issues,  ̶m̶i̶s̶s̶i̶n̶g̶ ̶d̶o̶c̶u̶m̶e̶n̶t̶a̶t̶i̶o̶n̶ ̶o̶r̶ ̶e̶v̶e̶n̶ ̶w̶i̶t̶h̶ ̶f̶a̶i̶l̶i̶n̶g̶ ̶u̶n̶i̶t̶-̶t̶e̶s̶t̶s̶.
Any annoying issue, requiring a bit more intelligence than usual might be tackled. 

In order to fix coding problems directly in your local filesystem, just type  
> hallux fix

If you want to fix issues in a orderly manner, where every fix has its own `git commit` run
> hallux fix --git

If you want `hallux` to propose you fixes and corrections directly into your Pull-Request, you may add following line into the CI
> hallux propose --github https://github.com/ORG_NAME/REPO_NAME/pull/ID 
`Hallux` will go to Github Web GUI and will send all its findings as comments with code proposals.

`> hallux agent --github_pr_id=${PULL_REQUEST}`
`will monitor your open Pull Request and answer to your comments, whenever you mention @hallux user in comment`

In order for `hallux` to understand your repo you need to provide `.hallux` configuration file, in the repo root folder.  
For more command-line commands and just type `$ hallux` or `$ hallux --help` 

# Coming features
In the future, following command will be added

If you want `hallux` to permanently monitor your `git branch` and send fixes whenever it finds any, you may start daemon right in your repo 
> hallux agent
`Hallux` will regularly pull latest changes and will push any appropriate fixes as separate commits.

> hallux review / simplify / refactor / annotate (docstrings)

** TDD Pair Programmer **
You may try to use `hallux` as your pair-coding buddy    
```
> hallux tdd-gtest Name-of-CMake-gtest-target  # FOR C++ Project 
> hallux tdd-pytest Name-of-pytest # FOR Python project
```

## Folder structure

* **python** main codes neural-nets, parsers, etc. 
* **scripts** complimentary scripts for managing the repo
* **src** c++ codes, also for sake of testing
* **tests** unit- and other tests for python and c++ parts of the code
* **worker** daemon app working as interface to external world 


## Installation

Execute
`./scripts/setup-python.sh`

You might need to add: `export PATH="/Path/to/hallux/bin:$PATH"`
into your `~/.bashrc` or `~/.zshrc` file

