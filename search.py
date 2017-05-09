#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import argparse
import sys
from collections import defaultdict 
from sets import Set

import bibtexparser as bibtex

import indexer

path='data/'
paths = sorted([os.path.join(path,fn) for fn in next(os.walk(path))[2]])

parser = argparse.ArgumentParser(description='Process some integers.')

parser.add_argument('--list-tags', nargs='?', const=True, default=False, help='List all known tags')

parser.add_argument('--words', metavar='<word>', type=str, nargs='+',
                      help='individual words to search for')

parser.add_argument('--tags', metavar='<tag>', type=str, nargs='+',
                      help='a list of comma separated tags to search for')

parser.add_argument('--years', metavar='<year>', type=str, nargs='+',
                      help='filter for specific years')

parser.add_argument('--authors', metavar='<author>', type=str, nargs='+',
                      help='a list of comma separated authors to search for')

args = parser.parse_args()

if args.list_tags:
   tags = []
   for filepath in [p for p in paths if p.endswith('.tags')]:
      data = open(filepath).read()
      for token in data.split('\n'):
         token = token.strip().lower()
         if len(token)>0:
            tags.append(token)
   for tag in sorted(set(tags)):
      print tag
   sys.exit(0)

words = []
tags = []
years = []
authors = []
if args.words:
   words = ' '.join(args.words)
   words = list(re.split('\W+', words))
if args.tags:
   tags = ' '.join(args.tags)
   tags = [tag.strip() for tag in tags.split(',')]
if args.years:
   years = ' '.join(args.years)
   years = list(re.split('\W+', years))
if args.authors:
   authors = ' '.join(args.authors)
   authors = [a.strip() for a in authors.split(',')]


index = indexer.loadIndex('data/')

wordsdoc = index['words']

answer = [os.path.basename(p)[:-4] for p in paths if p.endswith('.txt')]

##filter by word inside the documents
for word in words:
   if word.lower() in wordsdoc.keys():
      answer = Set(answer).intersection(Set(wordsdoc[word.lower()]))
      #print word,':',list(answer)
   else:
      print 'Word not found:',word

##Filter by tag

tagsdoc = index['tags']
tagFound = False
for tag in tags:
   if tag.lower() in tagsdoc.keys():
      answer = Set(answer).intersection(Set(tagsdoc[tag.lower()]))
      #print tag,':',list(answer)
      tagFound = True
   else:
      print 'Tag not found:',tag
if not tagFound:
   for tag in tags:
      for key in tagsdoc.keys():
         if tag.lower() in key:
            answer = Set(answer).intersection(Set(tagsdoc[key]))
            #print tag,'in',key,':',list(answer)

##Filter by author
new_answer = []
search_authors = [a.lower() for a in authors if a.strip().lower()!='and']
#print 'Authors:',search_authors
for paperid in sorted([int(pid) for pid in answer]):
   filepath = path+str(paperid)+'.bib'
   bibf = open(filepath)
   bib_database = bibtex.load(bibf)
   bibf.close()
   pauthors = [author.strip().lower() for author in re.split('\W',bib_database.entries[0]['author'])]
   if len(Set([a for a in pauthors if a!='and']).intersection(Set(search_authors)))>0:
      new_answer.append(paperid)
if authors and len(authors)>0:
   answer = new_answer

#print 'Answer:',list(answer)

for paperid in sorted([int(pid) for pid in answer]):
   filepath = path+str(paperid)+'.bib'
   bibf = open(filepath)
   bib_database = bibtex.load(bibf)
   bibf.close()
   if years and len(years)>0:
      if str(bib_database.entries[0]['year']) in years:
         print paperid,'\t',bib_database.entries[0]['title']
         print ' \t ',bib_database.entries[0]['author'],'('+str(bib_database.entries[0]['year'])+')'
      #else:
      #   print 'Year do not match:',paperid
   else:
      print paperid,'\t',bib_database.entries[0]['title']
      print ' \t ', (bib_database.entries[0]['author']).replace('\n','') ,'('+str(bib_database.entries[0]['year'])+')'
