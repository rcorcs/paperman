
import os.path

import textract

import bibtexparser as bibtex

class Paper:
    __pdf_file_path = None
    __bib_file_path = None
    __bib = None
    __cached_text = None
    note = None
    tags = []
    def __init__(self, pdf_file_path, bib_file_path=None):
        self.__pdf_file_path = pdf_file_path
        self.__bib_file_path = bib_file_path
        if self.__bib_file_path and os.path.isfile(self.__bib_file_path):
            with open(self.__bib_file_path) as f:
                self.__bib = bibtex.load(f)

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

    def tags(self):
        if self.__bib and 'tags' in self.__bib.entries[0].keys():
            return self.__bib.entries[0]['tags']
        return None

    def persist(self):
        if self.__bib:
            self.__bib.entries[0]['note'] = self.note
            self.__bib.entries[0]['tags'] = ';'.join(self.tags)
            writer = BibTexWriter()
            with open(self.__bib_file_path, 'w') as bibfile:
                bibfile.write(writer.write(db))
