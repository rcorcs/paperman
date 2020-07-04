
import os
import glob
import shutil
#import hashlib

import json

import re

from collections import defaultdict

from paper import *

class PaperBase:
    path = None
    
    entries = {}
    __indexed_ids = None
    __labels = None
    _words_index = None
    _tags_index = None

    def __init__(self, base_path):
        self.path = base_path
        if not os.path.exists(base_path+'/data'):
            os.makedirs(base_path+'/data')
        if os.path.exists(self.path+'/entries.json'):
            with open(self.path+'/entries.json') as f:
               self.entries = json.load(f)

        files = glob.glob(base_path+'/data/*.bib')
        paper_ids = [os.path.splitext(os.path.basename(path))[0] for path in files]
        if set(paper_ids)!=set(list(self.entries.keys())):
           self.entries = {}
           for bibtex_file in files:
              paper_id = os.path.splitext(os.path.basename(bibtex_file))[0]
              paper_files = glob.glob(base_path+'/data/'+paper_id+'.*')
              paper_file = [fn for fn in paper_files if fn!=bibtex_file][0]
              self.entries[paper_id] = (paper_file,bibtex_file)
           self.index(indexAll=True)
           self.persist()
        elif os.path.exists(self.path+'/index.json'):
            with open(self.path+'/index.json') as f:
                index = json.load(f)
                self.__indexed_ids = index['ids']
                self._words_index = index['words']
                self._tags_index = index['tags']

    def has_label(self, label):
       if not self.__labels:
          self.__labels = {}
          for paper_id in self.entries.keys():
             paper = self.paper(paper_id)
             self.__labels[paper.label()] = paper_id
       return (label in self.__labels.keys())

    def suggest_label(self, paper, update=False):
       label = str(re.split('\W+', paper.authors())[0].lower()) + str(paper.year())[-2:]
       if self.has_label(label) or self.has_label(label+'a'):
         if update and self.has_label(label):
            paper_id = self.label_to_id(label)
            paper = self.paper(paper_id)
            paper.label(label+'a')
            paper.persist()
            del self.__labels[label]
            self.__labels[paper.label()] = paper_id
         suffix = 'a'
         while self.has_label(label+suffix):
            suffix = chr(ord(suffix) + 1)
         label = label+suffix
       return label

    def label_to_id(self, label):
       if not self.__labels:
          self.__labels = {}
          for paper_id in self.entries.keys():
             paper = self.paper(paper_id)
             self.__labels[paper.label()] = paper_id
       if label in self.__labels.keys():
          return self.__labels[label]
       return None

#    def __next_id(self,paper_file=None):
#        return 'p'+str(len(self.entries))

    def insert(self,paper_file, bibtex_file):
        import hashlib
        with open(paper_file,'rb') as f:
          paper_id = hashlib.sha256(bytearray(f.read())).hexdigest()
        #paper_id = hashlib.sha256(len(self.entries)).hexdigest()
        #paper_id = self.__next_id()
        cp_paper_file = self.path+'/data/'+str(paper_id)+os.path.splitext(paper_file)[1]
        cp_bibtex_file = self.path+'/data/'+str(paper_id)+'.bib'
        shutil.copyfile(paper_file, cp_paper_file)
        shutil.copyfile(bibtex_file, cp_bibtex_file)
        paper = Paper(cp_paper_file,cp_bibtex_file)
        paper.label(self.suggest_label(paper, True))
        self.entries[paper_id] = (cp_paper_file,cp_bibtex_file)
        return (paper_id, paper)

    def remove(self, paper_id):
        if paper_id in self.entries.keys():
           del self.entries[paper_id]
           self.__remove_from_index(paper_id)

    def __remove_from_index(self, paper_id):
        self.__indexed_ids = list(filter((paper_id).__ne__, self.__indexed_ids))
        for k in self._words_index.keys():
           self._words_index[k] = list(filter((paper_id).__ne__, self._words_index[k]))
        for k in self._tags_index.keys():
           self._tags_index[k] = list(filter((paper_id).__ne__, self._tags_index[k]))

    def persist(self):
        with open(self.path+'/entries.json','w') as f:
           json.dump(self.entries,f)
        with open(self.path+'/index.json','w') as f:
            index = {'ids':self.__indexed_ids,'tags':self._tags_index,'words':self._words_index}
            json.dump(index,f)

    def paper(self, paper_id):
        if paper_id not in self.entries.keys():
            return None
        paper_path, bibtex_path = self.entries[paper_id]
        return Paper(paper_path, bibtex_path)

    def index(self,indexAll=False,re_index=[]):
        index = None
        #if os.path.exists(self.path+'/index.pkl'):
        #    with open(self.path+'/index.pkl') as f:
        #        index = pickle.load(f)
        #        self.__indexed_ids = index['ids']
        #        self._words_index = index['words']
        #        self._tags_index = index['tags']
        if indexAll:
            re_index = self.entries.keys()
        self.__update_index(re_index)
        with open(self.path+'/index.json','w') as f:
            index = {'ids':self.__indexed_ids,'tags':self._tags_index,'words':self._words_index}
            json.dump(index,f)

    def __update_index(self, re_index=[]):
        if not self.__indexed_ids:
            self.__indexed_ids = []
        if not self._words_index:
            self._words_index = defaultdict(list)
        if not self._tags_index:
            self._tags_index = defaultdict(list)

        knownIds = [pid for pid in self.__indexed_ids if pid not in re_index]
        self.__indexed_ids = list(self.entries.keys())
        if set(knownIds)!=set(self.entries.keys()):
            indexingList = sorted([pid for pid in self.entries.keys() if pid not in knownIds])
            #print 'Indexing:',' '.join([str(fid) for fid in indexingList])
            for paper_id in indexingList:
                print(paper_id)
                paper = self.paper(paper_id)
                #words indexing
                text = paper.text()
                if text:
                    #TODO: filter stopwords and do some other text processing
                    filtered_text = [w for w in re.split('\W+', str(text)) if len(w)>1 and (not w.isdigit())]
                    for token in filtered_text:
                        if token.lower() not in self._words_index.keys():
                             self._words_index[token.lower()] = [];
                        if paper_id not in self._words_index[token.lower()]:
                            self._words_index[token.lower()].append(paper_id)
                            #cleanup
                    for k in self._words_index.keys():
                        self._words_index[k] = list(set(self._words_index[k]))

                #tag indexing
                for tag in paper.tags:
                    if paper_id not in self._tags_index[tag.lower()]:
                        self._tags_index[tag.lower()].append(paper_id)
                        #cleanup
                for k in self._tags_index.keys():
                    self._tags_index[k] = list(set(self._tags_index[k]))
