#!/bin/bash
DATA=./data

vim $DATA/$1.tags

python indexer.py $1
