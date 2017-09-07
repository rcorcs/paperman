
from paperbase import *

class PaperView:
    __filtered_ids = None
    __base = None

    def __init__(self, base):
        self.__filtered_ids = base.entries.keys()
        self.__base = base
        self.__base.index()

    ##filter by word inside the documents
    def filterByWords(self, words, conjunction=True):
        if conjunction:
            answer = self.__filtered_ids
        else:
            answer = Set()
        #TODO: filter stopwords and do some other text processing
        filtered_words = [w for w in re.split('\W+', ' '.join(words)) if len(w)>1 and (not w.isdigit())]
        foundAny = False
        for word in words:
            if word.lower() in self.__base._words_index.keys():
                foundAny = True
                if conjunction:
                    answer = Set(answer).intersection(Set(self.__base._words_index[word.lower()]))
                else:
                    answer = Set(entries.keys()).union(Set(self.__base._words_index[word.lower()]))
        if not foundAny:
            answer = Set()
        self.__filtered_ids = list(answer)

    ##Filter by tags
    def filterByTags(self, tags, conjunction=True):
        if conjunction:
            answer = self.__filtered_ids
        else:
            answer = Set()
        foundAny = False
        for tag in tags:
            if tag.lower() in self.__base._tags_index.keys():
                foundAny = True
                if conjunction:
                    answer = Set(answer).intersection(Set(self.__base._tags_index[tag.lower()]))
                else:
                    answer = Set(entries.keys()).union(Set(self.__base._tags_index[tag.lower()]))
        if not foundAny:
            answer = Set()
        self.__filtered_ids = list(answer)

    ##Filter by authors
    def filterByAuthors(self, authors, conjunction=True):
        pass

    def filterByYears(self, years):
        pass

    def papers(self):
        filteredPapers = {}
        #print self.__filtered_ids
        for paper_id in self.__filtered_ids:
            p = self.__base.paper(paper_id)
            filteredPapers[paper_id] = p
        return filteredPapers
