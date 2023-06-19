# hallux - Convenient Coding Assistant

`Hallux` is a smart utility to help you with routine coding tasks. It may help you with compilation errors, linting or type-check issues, missing documentation or even with failing unit-tests.      
Any annoying issue, requiring a bit more intelligence than usual might be tackled. 

In order to fix coding problems directly in your repo, just type  
> hallux fix  

If you want to fix issues in a orderly manner, where every fix has its own `git commit` run
> hallux fix --commit  # or hallux fix -C 

If you want `hallux` to propose you fixes and corrections directly into your Pull-Request, you may add following line into the CI
> hallux propose --pull-request=${PULL_REQUEST}

`Hallux` will go to Github Web GUI and will send all its findings as comments with proposals.

If you want `hallux` to permanently monitor your `git branch` and send fixes whenever it finds any, you may start daemon right in your repo 
> hallux agent

`Hallux` will regularly pull latest changes and will push any appropriate fixes as separate commits.

In order for `hallux` to understand your repo you need to provide `.hallux` configuration file, in the repo root folder.  
For more command-line commands and just type `$ hallux` or `$ hallux --help` 

In the future,  following command will be added

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


  
  
  
