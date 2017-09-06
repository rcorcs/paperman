#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys

from collections import defaultdict
from sets import Set

import argparse
import pickle

import bibtexparser as bibtex

def performIndex(basepath, currentIndex=None, reIndex=None):
   paths = sorted([os.path.join(basepath,fn) for fn in next(os.walk(basepath))[2]])

   if reIndex==None:
      reIndex = []
   knownIds = []
   wordsdoc = defaultdict(list)
   tagsdoc = defaultdict(list)
   if currentIndex:
      knownIds = [fid for fid in currentIndex['ids'] if fid not in reIndex]
      wordsdoc = currentIndex['words']
      tagsdoc = currentIndex['tags']

   ids = []
   for filepath in [p for p in paths if p.endswith('.pdf')]:
      ids.append(os.path.basename(filepath)[:-4])

   if set(ids)!=set(knownIds):
      indexingList = sorted([int(fid) for fid in ids if fid not in knownIds])
      print 'Indexing:',' '.join([str(fid) for fid in indexingList])
      #words indexing
      for filepath in [p for p in paths if p.endswith('.txt')]:
         fid = os.path.basename(filepath)[:-4]
         if fid in knownIds:
            continue
         data = open(filepath).read()
         for token in re.split('\W+', data):
            if filepath not in wordsdoc[token.lower()]:
               wordsdoc[token.lower()].append(fid)
      for k in wordsdoc.keys():
         wordsdoc[k] = list(set(wordsdoc[k]))

      #tag indexing
      for filepath in [p for p in paths if p.endswith('.tags')]:
         fid = os.path.basename(filepath)[:-5]
         if fid in knownIds:
            continue
         data = open(filepath).read()
         for token in data.split('\n'):
            token = token.strip().lower()
            if len(token)>0 and filepath not in tagsdoc[token]:
               tagsdoc[token].append(fid)
      for k in tagsdoc.keys():
         tagsdoc[k] = list(set(tagsdoc[k]))

   index = {'ids':ids, 'words':wordsdoc, 'tags':tagsdoc}
   return index

def loadIndex(basepath):
   index = None
   if os.path.exists(basepath+'index.dat'):
      with open(basepath+'index.dat') as f:
         index = pickle.load(f)
   index = performIndex(basepath,index)
   return index

if __name__=='__main__':
   index = None
   if os.path.exists('data/index.dat'):
      with open('data/index.dat') as f:
         index = pickle.load(f)
   index = performIndex('data/',index, sys.argv[1:])
   with open('data/index.dat','w') as f:
      pickle.dump(index,f)
