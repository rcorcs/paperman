
import os.path

import textract

import bibtexparser as bibtex
from bibtexparser.bwriter import BibTexWriter

class Paper:
    __pdf_file_path = None
    __bib_file_path = None
    __bib = None
    __cached_text = None
    note = ''
    tags = []
    def __init__(self, pdf_file_path, bib_file_path=None):
        self.__pdf_file_path = pdf_file_path
        self.__bib_file_path = bib_file_path
        if self.__bib_file_path and os.path.isfile(self.__bib_file_path):
            with open(self.__bib_file_path) as f:
                self.__bib = bibtex.load(f)
                if 'note' in self.__bib.entries[0].keys():
                    self.note = self.__bib.entries[0]['note']
                if 'tags' in self.__bib.entries[0].keys():
                    tags = self.__bib.entries[0]['tags'].split(';')
                    self.tags = [t.strip() for t in tags]
    def text(self):
        if not self.__cached_text:
            self.__cached_text = textract.process(self.__pdf_file_path)
        return self.__cached_text

    def __str__(self):
        #return self.text()
        return '\t"{}"\n\t{} ({})'.format(str(self.title()),str(self.authors()),str(self.year()))

    def title(self):
        if self.__bib:
            return self.__bib.entries[0]['title']
        return None

    def year(self):
        if self.__bib:
            return self.__bib.entries[0]['year']
        return None

    def authors(self):
        if self.__bib:
            return self.__bib.entries[0]['author']
        return None

    def bibtex(self,simplified=False):
        if not self.__bib:
            return None
        from copy import deepcopy
        bib = deepcopy(self.__bib)
        if 'note' in bib.entries[0].keys():
            del bib.entries[0]['note']
        if 'tags' in bib.entries[0].keys():
            del bib.entries[0]['tags']
        if simplified:
            for k in ['doi','acmid','isbn', 'url','link']:
                if k in bib.entries[0].keys():
                    del bib.entries[0][k]
        writer = BibTexWriter()
        return writer.write(bib).strip()

    def persist(self):
        if self.__bib:
            self.__bib.entries[0]['note'] = self.note
            self.__bib.entries[0]['tags'] = ';'.join(self.tags)
            writer = BibTexWriter()
            with open(self.__bib_file_path, 'w') as bibfile:
                bibfile.write(writer.write(self.__bib))
