#!/bin/bash

#time python ws_normalize.py --srcdir /hg191/corpora/accessible-v3.0/ --tgtdir /hg191/corpora/clean-accessible-v3.0/ --gramfiles /hg191/corpora/google-ngrams/en.1M.filtered.1g /hg191/corpora/google-ngrams/en.1M.filtered.2g /hg191/corpora/google-ngrams/en.1M.filtered.3g --debugfile /hg191/corpora/clean-accessible-v3.0/summary.jsonl


SRC_PARENT=/hg191/corpora/accessible-v3.0
TGT_PARENT=/hg191/corpora/clean-accessible-v3.0
GRAM_DIR=/hg191/corpora/google-ngrams

G1_FILE=$GRAM_DIR/en.1M.filtered.1g
G2_FILE=$GRAM_DIR/en.1M.filtered.2g
G3_FILE=$GRAM_DIR/en.1M.filtered.3g

parallel python -u ws_normalize.py --srcdir $SRC_PARENT/{} --tgtdir $TGT_PARENT/{} --gramfiles $G1_FILE $G2_FILE $G2_FILE --debugfile $TGT_PARENT/{}/summary.jsonl ::: $(ls $SRC_PARENT) 
