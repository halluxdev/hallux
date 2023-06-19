
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
4. We can use compilation error messages as extra input for our Net, which is not possible in scripting languages
5. C++ is widely popular programming language, used by many rich companies (and individuals)
6. I love C++ more than any other :)) 

## TRANSFORMER IDEAS

1. Take existing Transformer, like BERT (or its descendant) and fine-tune it for our problem
2. We may extend existing BERT tokens with tokens coming directly from C++ parser. This will help to learn c++ syntax, and thus probably reduce training costs.
3. We may introduce even "bigger" artificial tokens like #include<some-standard-library>. In this way BERT might also learn how includes affect existing (exposed) functions/classes.
4. In the data preparation stage we may embed local include files into cpp files, such that whole context is available. This might be a problem though, as such files could be arbitrary large
5. We may play with External Attention (which may reduce training cost, if we decide to train from scratch)
6. KD-Tree Attention with O(N Log N) complexity ? Sparse Attention + Kd Tree looks like an option
   Классический аттеншен "посещает" (софтмаксит) все предыдущие токены. Что если мы скажем что вместо всех N мы тебе подсунем M (M << N) наиболее релевантных. Эдакий софтмакс на минималках. Key and Query высчитываются по предыдущим значениям весов, так что можно сказать чито все Key и все Query мы можем посчитать отдельно за время 2N. Все Keys складываем в KD-Tree (тут уже N * Log N)  и для всех Query лазаем в KDTree и собираем M самых близких (в евклидовом смысле)
   Дот-продукт собственно и дает самые большие значения самым близким векторам. Вот мы ему их и подсунем

## Abstract Syntax Tree (AST-NN)
* We may "directly" use AST as trainable structure, which has "Branch" and "Leaf" Nodes of different kinds
* Each kind of node may have their own trainable weights, and thus aggregate information differently.
* Each C++ file contains different AST tree structure, but they built of the same kinds of "Branches" and "Leafs", thus training on many different datasets (i.e. cpp files) is not a problem
* It is possible to process whole `Translation Unit`, which has all the context we ever need to fix compilation error
* Common includes like #include<string> may be extracted as separatly trainable "Branch" Nodes, which after a while may be fixed and serve as pre-trained standard library things. This would simplify inference later on.
* We may traverse the whole AST in linear time, aggregating information about everything in one root node. We may specifically add plenty of meat (floats) there.
* After aggrergation we may traverse back from-top-to-bottom (maybe with interconnects like in U-NET) fashion in order to classify each node
* AST-NN looks like more efficient and easier way to process huge c++ files than a transformer
* We may emulate trainable Attention mechanisms, by sending messages between nodes

**idea 2:**
- CNN is like Finite-response Linear filter with trainable kernel
- RNN is like Infinite-response LF
- Transformer is more like trainable Non-local means filter, and that's why it's computationally complex and can only have limited kernel size
- we may combine these ideas with the fact that AST has a tree-structure

**idea 3:**
how to turn tree-like NN into a generative language model?
- Add [UNKNOWN], [EXCESSIVE] Nodes (or Leaf Kinds)
- Train to classify each Normal Node if its [EXCESSIVE] or not
- Train to classify what Kind each [UNKNOWN] node must have (it could be also [EXCESSIVE], why not)
- During training we add (introduce) some percent of wrong nodes and then require to classify them as [EXCESSIVE]
- During training we remove some nodes and add two or more [UNKNOWN] instead, and require to classify them
- During inference we shall detect what place(s) is/are broken, using compiler output, and put some [UNKNOWN] nodes in that area.
    - In this way trained NN will try to remove any shit it finds excessive and convert several [unkonwn] nodes to those which it thinks shall be there

**Idea to try**
https://huggingface.co/models?pipeline_tag=fill-mask
1. Choose most relevant FILL-MASK model
2. Fine-tune with C++ corpus
3. On inference with real problem we use compilation error message to find list of tokens around the error
4. ...
5. PROFIT!!

**another stupid idea to try**
Once we have large c++ corpus and (custom?) tokenizer we may easily train markov-process probability table.
This is already most stupid, but extremely fast language model. Compiler is binary, and if we not using any optimization compilation is relatively fast too. We may generate billion of variants of code and choose the one, what successfully compiled. Everything is on CPU :)

**Test-Driven-Development Assistant: Как бороться с огромным контекстом (token count) в коде?**
Когда мы хотим подправить функцию так чтобы она удолетворяла новому unit-test нам (вроде-бы) нужно знать весь проект с кодом.   
Но на самом деле не весь. Чаще всего ошибку можно пофиксить зная только саму функцию (и ее сигнатуру) в которой ошибка.
Если этого не достаточно, значит нужны сигнатуры других функций, которые есть в области видимости.
Короче говоря - идея заключается не в том чтобы использовать AST чтобы трейнить ИИ на дереве, а использовать AST чтобы выкинуть весь ненужный для текущей проблемы код.
Если мы зараннее знаем какой у нас лимит по токенам, мы в первую очередь вырезаем из AST функцию которую надо фиксить, плюс все юнит-тесты.
Затем если лимит позволяет мы добавляем сигнатуры других функций/классов которые могут быть релевантны. Ну и сортируем их по важности. Сперва самые на наш взгляд важнве, потом все менее и менее важные.  




