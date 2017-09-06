
import os
#import glob
import shutil
#import hashlib
import pickle

from paper import *

class PaperBase:
    base_path = None
    entries = {}

    def __init__(self, base_path):
        self.base_path = base_path
        if not os.path.exists(base_path+'/data'):
            os.makedirs(base_path+'/data')
        if os.path.exists(self.base_path+'/entries.pkl'):
            with open(self.base_path+'/entries.pkl') as f:
               self.entries = pickle.load(f)

    def __next_id(self,paper_file=None):
        return 'id_'+str(len(self.entries))

    def insert(self,paper_file, bibtex_file):
        #paper_id = hashlib.sha256(str(len(self.entries))).hexdigest()
        paper_id = self.__next_id()
        cp_paper_file = self.base_path+'/data/'+str(paper_id)+os.path.splitext(paper_file)[1]
        cp_bibtex_file = self.base_path+'/data/'+str(paper_id)+'.bib'
        shutil.copyfile(paper_file, cp_paper_file)
        shutil.copyfile(bibtex_file, cp_bibtex_file)
        paper = Paper(cp_paper_file,cp_bibtex_file)
        self.entries[paper_id] = (cp_paper_file,cp_bibtex_file)
        return paper

    def persist(self):
        with open(self.base_path+'/entries.pkl','w') as f:
           pickle.dump(self.entries,f)
