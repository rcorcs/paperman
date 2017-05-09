#!/bin/bash
DATA=./data
mkdir -p $DATA

vim $DATA/$1.tags

python indexer.py $1
