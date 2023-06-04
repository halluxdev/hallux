# hallux
AI code generator for C++

idea 1:
For transformer-like architecure we may combine tokens coming from AST and tokens coming from spelling into one stream, by using binary flag (one hot) in the token and constraining both embeddigs to be the same size.

idea 2:
- CNN is like Finite-response Linear filter with trainable kernel
- RNN is like Infinite-response LF 
- Transformer is more like trainable Non-local means filter, and that's why it's computationally complex and can only have limited kernel 
- we may combine these ideas with the fact that code has tree-structure

idea 3:
how to turn tree-like structure into a language model?
- first train network on a tree, to predict node type, then stop and train transformers, using input data from previos fixed net
- 
- rather than using transformer directly we may use trainable NLM filter with custom "attention" heads 
- we may have 2 passes up-down and down-up

