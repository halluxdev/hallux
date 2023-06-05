# hallux
**AI code generator for C++**
For now, we're only aiming at automatic fixing of compilation errors.
*In the future generation of new code (in TDD-like manner) is also planned.

## Motivation
Existing Code-Gen Neural Nets are working in GPT-style (aka Transformer Decoder, aka Continuation Language Model). I.e. they're predicting next tokens, taking into account existing ones.
This is great approach to write a new function from the scratch, but in real *Software Enginering* life, main complexity lies in the understanding of large corpus of the existing code and applying small appropriate patches to it.
Another problem with Transformer architectures is that they able to access only token sequencies of a fixed maximum length.

For the useful code generator tool it is essential to understand the "whole scope" of the code it is working with, but more importantly is ability to modify existing and introduce new tokens in the arbitrary place within the code.
Therefore, instead applying *Transformer Decoder* architectures we might try to use *Transformer Encoder* ones, like BERT and its descendants. 

### Why C++
Unlike scripting languages like Python, C++ has a compiler which instantly brings number of important benefits.

1. Ability to fix such errors brings important customer value
2. Compilation result (failed or pass) also brings super-easy ability to train our networks in semi-supervised manner
3. Compilation result can also be used during inference (code generation) stage, when we check CodeGen results for validity. Even if neural net provides low performance with small probability of success we still able to repeat CodeGen multiple times until success. 

## Folder structure

* **python** main codes neural-nets, parsers, etc. 
* **scripts** complimentary scripts for managing the repo
* **src** c++ codes, also for sake of testing
* **tests** unit- and other tests for python and c++ parts of the code
* **worker** daemon app working as interface to external world 

### Worker

Clones repository defined in the config file, runs the build and reacts on the compilation results

`> python worker/worker.py`


**idea 1:**
For transformer-like architecure we may combine tokens coming from AST and tokens coming from spelling into one stream, by using binary flag (one hot) in the token and constraining both embeddigs to be the same size.

**idea 2:**
- CNN is like Finite-response Linear filter with trainable kernel
- RNN is like Infinite-response LF 
- Transformer is more like trainable Non-local means filter, and that's why it's computationally complex and can only have limited kernel 
- we may combine these ideas with the fact that code has tree-structure

**idea 3:**
how to turn tree-like structure into a language model?
- first train network on a tree, to predict node type, then stop and train transformers, using input data from previos fixed net
- 
- rather than using transformer directly we may use trainable NLM filter with custom "attention" heads 
- we may have 2 passes up-down and down-up
