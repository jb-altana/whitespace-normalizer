# Whitespace Normalization

### Problem

Given a non-standard term **t** (eg. _Senatoradmits_), split the term into two words **a** (Senator) and **b**(admits) such that both **a** and **b** are valid terms. 

This project aims to build simple lightweight systems that uses N-gram counts and likelihood ratios to address this problem.

### Approach
Refer to this [note](http://markdownnotes.com/app/#/?note=20819) to see the basic math of the underlying approach.

### Code and Data

- The `modules` directory contains the code for the implementation of all the models described in the note.
- The `examples` directory contains a jupyter notebook which demonstrates how the approach works in practice.

### Contact
sandeepsoni@gatech.edu

### TODO
(a) Improve the readability of the code
(b) Add a command line script to demonstrate how it works on a corpus on the entire document.
(c) Include more description of the code in the README file.
(d) Add evaluation scripts, annotations and results from the paper if it gets accepted.
