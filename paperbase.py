
import os
#import glob
import shutil
#import hashlib
import pickle

import re

from collections import defaultdict
from sets import Set

from paper import *

class PaperBase:
    path = None
    entries = {}
    __indexed_ids = None
    _words_index = None
    _tags_index = None

    def __init__(self, base_path):
        self.path = base_path
        if not os.path.exists(base_path+'/data'):
            os.makedirs(base_path+'/data')
        if os.path.exists(self.path+'/entries.pkl'):
            with open(self.path+'/entries.pkl') as f:
               self.entries = pickle.load(f)
        if os.path.exists(self.path+'/index.pkl'):
            with open(self.path+'/index.pkl') as f:
                index = pickle.load(f)
                self.__indexed_ids = index['ids']
                self._words_index = index['words']
                self._tags_index = index['tags']

    def __next_id(self,paper_file=None):
        return 'p'+str(len(self.entries))

    def insert(self,paper_file, bibtex_file):
        #paper_id = hashlib.sha256(str(len(self.entries))).hexdigest()
        paper_id = self.__next_id()
        cp_paper_file = self.path+'/data/'+str(paper_id)+os.path.splitext(paper_file)[1]
        cp_bibtex_file = self.path+'/data/'+str(paper_id)+'.bib'
        shutil.copyfile(paper_file, cp_paper_file)
        shutil.copyfile(bibtex_file, cp_bibtex_file)
        paper = Paper(cp_paper_file,cp_bibtex_file)
        self.entries[paper_id] = (cp_paper_file,cp_bibtex_file)
        return paper

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
        with open(self.path+'/entries.pkl','w') as f:
           pickle.dump(self.entries,f)
        with open(self.path+'/index.pkl','w') as f:
            index = {'ids':self.__indexed_ids,'tags':self._tags_index,'words':self._words_index}
            pickle.dump(index,f)

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
        with open(self.path+'/index.pkl','w') as f:
            index = {'ids':self.__indexed_ids,'tags':self._tags_index,'words':self._words_index}
            pickle.dump(index,f)

    def __update_index(self, re_index=[]):
        if not self.__indexed_ids:
            self.__indexed_ids = []
        if not self._words_index:
            self._words_index = defaultdict(list)
        if not self._tags_index:
            self._tags_index = defaultdict(list)

        knownIds = [pid for pid in self.__indexed_ids if pid not in re_index]
        self.__indexed_ids = self.entries.keys()
        if set(knownIds)!=set(self.entries.keys()):
            indexingList = sorted([pid for pid in self.entries.keys() if pid not in knownIds])
            print 'Indexing:',' '.join([str(fid) for fid in indexingList])
            for paper_id in indexingList:
                paper = self.paper(paper_id)
                #words indexing
                text = paper.text()
                if text:
                    #TODO: filter stopwords and do some other text processing
                    filtered_text = [w for w in re.split('\W+', text) if len(w)>1 and (not w.isdigit())]
                    for token in filtered_text:
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
