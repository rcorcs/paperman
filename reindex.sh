#!/bin/bash

DATA=./data
mkdir -p $DATA
rm -f ./data/index.dat
python indexer.py

