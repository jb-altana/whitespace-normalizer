# Whitespace Normalization

### Problem

Given a non-standard term **t** (eg. _Senatoradmits_), split the term into two words **a** (Senator) and **b**(admits) such that both **a** and **b** are valid terms. 

This project aims to build simple lightweight systems that use N-gram counts and likelihood ratios to address this problem.

### Approach
Refer to our [paper](https://www.aclweb.org/anthology/W19-2513.pdf) to understand our approach to solving the problem.
This [note](http://markdownnotes.com/app/#/?note=20819) shows the basic math in even greater detail.

### Code and Data

- The `modules` directory contains the code for the implementation of all the models described in the note.
- The `examples` directory contains a jupyter notebook which demonstrates how the approach works in practice.

### Contact
sandeepsoni@gatech.edu

### Reference
Please cite our paper if you end up using the code of this repository.

```
@inproceedings{soni2019correcting,
  title={Correcting Whitespace Errors in Digitized Historical Texts},
  author={Soni, Sandeep and Klein, Lauren and Eisenstein, Jacob},
  booktitle={Proceedings of the 3rd Joint SIGHUM Workshop on Computational Linguistics for Cultural Heritage, Social Sciences, Humanities and Literature},
  pages={98--103},
  year={2019}
}
```

### TODO
- Update this README about the organization of the code once its stable.
- Improve the readability of the code.
- Include more description of the code in the README file.
- Add evaluation scripts, annotations and results from the paper when accepted.
