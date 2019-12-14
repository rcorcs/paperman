import argparse

import re
import operator

import unicodedata

import sys

def strip_accents(unicode_string):
  """
  Strip accents (all combining unicode characters) from a unicode string.
  """
  ndf_string = unicodedata.normalize('NFD', unicode_string)
  is_not_accent = lambda char: unicodedata.category(char) != 'Mn'
  return ''.join(
    char for char in ndf_string if is_not_accent(char)
  )

def FormatInsitution(name):
  skip = ['and', 'at','the','a','an','de','of','in']
  name = strip_accents(unicode(name.strip().lower(), "utf-8"))
  tokens = re.split('\W+',name)
  valid = []
  for t in tokens:
    if t not in skip:
      valid.append(t)
  return ' '.join(valid)

def FormatAuthor(name):
  name = strip_accents(unicode(name.strip().lower(), "utf-8"))
  tokens = re.split("[^a-zA-Z0-9_\']+",name)
  s = ''
  if len(tokens)>1:
    s += tokens[0].capitalize()
    if len(tokens[0])==1:
      s += '.'
  if len(tokens)>0:
    s += ' '+tokens[-1].capitalize()
    if s.find('\'')>=0:
      news = ''
      FoundMarker = False
      for c in s:
        if FoundMarker:
          news += c.capitalize()
        else:
          news += c
        FoundMarker = False
        if c == '\'':
          FoundMarker = True
      s = news
    return s
  else:
    return None

aliases = {}
with open('Aliases.txt') as f:
  for line in f:
    line = line.strip()
    if len(line)>0:
      tmp = line.split(':')
      key = tmp[0].strip()
      others = tmp[1].split(';')
      formated = [FormatInsitution(key)]
      for val in others:
        formated.append(FormatInsitution(val))
      aliases[key] = list(set(formated))

def GetInsitutionName(name,aliases):
  formated = FormatInsitution(name)
  for k in aliases.keys():
    if formated in aliases[k]:
      return k
  return name.strip()

def FindInsitutionName(name,aliases):
  formated = FormatInsitution(name)
  for k in aliases.keys():
    if formated in aliases[k]:
      return k
  return None


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('confs', metavar='ConfName', type=str, nargs='+', help='a list of conference names')
parser.add_argument('-t', '--top', metavar='Top', default=1000000, type=int, help='number of items to show in the top rank')
parser.add_argument('-a','--authors', metavar='Author', type=str, nargs='+', help='a list of author names to filter')
args = parser.parse_args()
confnames = args.confs
top = args.top
authnames = args.authors
#print confnames
#print top
#confnames = sys.argv[1:]
#top = 1000000
#if len(sys.argv)>2:
#  top = int(sys.argv[2])

years = []
papers = []
for confname in confnames:
  with open(confname+'.txt') as f:
    year = None
    title = None
    authors = []
    entry = None
    for line in f:
      line = line.strip()
      tmp = line.split()
      if len(line)>0:
        if len(tmp)==2 and tmp[0]==confname and tmp[1].strip().isdigit():
          year = int(tmp[1].strip())
          years.append(year)
        elif title==None:
          title = line
          entry = {}
          entry['title'] = title
          entry['authors'] = []
          entry['year'] = year
        else:
          if line[-1]==')':
            institution = line[line.find('(')+1:].strip(')')
            if ',' in institution:
              institution = institution.split(',')[0].strip()
            authors = line[:line.find('(')].split(',')
            if FindInsitutionName(institution,aliases)==None:
              aliases[institution] = [FormatInsitution(institution)]
            for auth in authors:
              if len(auth.strip())>0:
                entry['authors'].append( {'name':auth.strip(), 'institution':institution} )
      else:
        if entry!=None:
          papers.append( entry )
        title = None
        authors = []
        entry = None
years = list(set(years))

instFreq = {}
for paper in papers:
  listOfInsts = []
  for author in paper['authors']:
    listOfInsts.append(GetInsitutionName(author['institution'],aliases))
  for inst in set(listOfInsts):
    if inst not in instFreq.keys():
      instFreq[inst] = 1
    else:
      instFreq[inst] += 1

for y in years:
  seen1stAuthor = []
  for paper in papers:
    if paper['year']==y:
      if len(paper['authors'])==0:
        print 'Unexpected:',str(paper)
        continue
      if paper['authors'][0] in seen1stAuthor:
        #print 'Found:',y,paper['authors'][0]
        pass
      else:
        seen1stAuthor.append(paper['authors'][0])

print 'Institutions:'
ranked = list(reversed(sorted(instFreq.items(), key=operator.itemgetter(1))))[:top]
counter = 1
for entry in ranked:
  print ("%d.\t%s  (%d)" % (counter, entry[0], entry[1]))
  counter += 1

authFreq = {}
for paper in papers:
  listOfAuthors = []
  for author in paper['authors']:
    name = FormatAuthor(author['name'])
    if name:
      listOfAuthors.append(name)
  for author in set(listOfAuthors):
    if author not in authFreq.keys():
      authFreq[author] = 1
    else:
      authFreq[author] += 1

print ''
print 'Authors:'

ranked = list(reversed(sorted(authFreq.items(), key=operator.itemgetter(1))))

topranked = ranked[:top]
counter = 1
for entry in topranked:
  print ("%d.\t%s  (%d)" % (counter, entry[0], entry[1]))
  counter += 1

counter = 1
for entry in ranked:
  if sum( [1 if val in entry[0].split() else 0 for val in authnames] )>0 and counter>top:
    print ("%d.\t%s  (%d)" % (counter, entry[0], entry[1]))
  counter += 1

