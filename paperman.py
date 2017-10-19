import sys
import os
import shutil
import tempfile

from subprocess import call

import argparse
import configparser

from paper import *
from paperbase import *
from paperfilter import *


db = None

def prompt_editor(file_path):
    EDITOR = os.environ.get('EDITOR','vim') #that easy!
    initial_text = '' # if you want to set up the file somehow
    if os.path.isfile(file_path):
        with open(file_path) as f:
            initial_text = f.read()
    call([EDITOR, file_path])

def read_from_editor(initial_text=''):
    EDITOR = os.environ.get('EDITOR','vim') #that easy!
    edited_text = None
    with tempfile.NamedTemporaryFile(suffix=".paperman.tmp") as tf:
        tf.write(initial_text)
        tf.flush()
        call([EDITOR, tf.name])
        tf.seek(0)
        edited_text = tf.read()
    return edited_text

def run_add_paper():
    parser = argparse.ArgumentParser(description='Paper Manager [add]')
    parser.add_argument('paper_file', type=str, nargs=1, help='path to the paper''s file')
    parser.add_argument('bibtex_file', type=str, nargs='?', help='path to the paper''s BibTeX file')
    args = parser.parse_args(sys.argv[2:])
    #print args
    #print args.paper_file
    paper = None

    if args.bibtex_file:
        paper = db.insert(args.paper_file[0],args.bibtex_file)
    else:
        _, path = tempfile.mkstemp(suffix=".paperman.tmp")
        prompt_editor(path)
        paper = db.insert(args.paper_file[0],path)
        os.remove(path)
    print paper.text()[:100]
    print paper.title()
    print paper.authors()
    print paper.year()
    db.persist()
    return paper

def run_update():
    parser = argparse.ArgumentParser(description='Paper Manager [update]')
    parser.add_argument('field', type=str, nargs=1, help='filed to be updated: note\ttags\tbibtex')
    parser.add_argument('paper_id', type=str, nargs=1, help='paper id to be updated')
    args = parser.parse_args(sys.argv[2:])

    field = args.field[0]
    paper_id = args.paper_id[0]
    if paper_id in db.entries.keys():
        paper = db.paper(paper_id)
        if field   == 'bibtex':
            prompt_editor(paper.bibtexFile())
        elif field   == 'note':
            paper.note = read_from_editor(paper.note)
        elif field == 'tags':
            tags = read_from_editor('\n'.join(paper.tags))
            splitted_tags = [tag.strip() for tag in re.split('[\n,;]',tags.strip())]
            paper.tags = splitted_tags
        paper.persist()
        db.index(re_index=[paper_id])

def run_search():
    #print db.entries
    parser = argparse.ArgumentParser(description='Paper Manager [list]')
    #search/list command
    #parser.add_argument('--list-tags', nargs='?', const=True, default=False, help='List all known tags')
    parser.add_argument('--words', metavar='<word>', type=str, nargs='+',
                          help='individual words to search for')
    parser.add_argument('--tags', metavar='<tag>', type=str, nargs='+',
                          help='a list of comma separated tags to search for')
    parser.add_argument('--years', metavar='<year>', type=str, nargs='+',
                          help='filter for specific years')
    parser.add_argument('--authors', metavar='<author>', type=str, nargs='+',
                          help='a list of comma separated authors to search for')
    parser.add_argument('--bibtex', nargs='?', const=True, default=False, help='List in BibTeX format')
    parser.add_argument('--clean-output', nargs='?', const=True, default=False, help='Produce a simplified output')
    args = parser.parse_args(sys.argv[2:])
    view = PaperView(db)
    if args.words:
        #words = list(re.split('\W+', args.words))
        words = args.words
        view.filterByWords(words)
    if args.tags:
        tags = ' '.join(args.tags)
        tags = [tag.strip() for tag in re.split('[,;]',tags.strip())]
        view.filterByTags(tags)
    if args.years:
        years = ' '.join(args.years)
        years = list(re.split('\W+', years))
        view.filterByYears(years)
    if args.authors:
        authors = ' '.join(args.authors)
        authors = [a.strip() for a in re.split('[,;]',authors.strip())]
        view.filterByAuthors(authors)
    asBibtex = args.bibtex
    simplified = args.clean_output
    for k, paper in view.papers().items():
        if asBibtex:
            print paper.bibtex(simplified)
        else:
            print k, paper

if __name__=='__main__':
    base_path = os.environ.get('HOME','.')+'/.paperman'
    db = PaperBase(base_path)
    #print sys.argv
    parser = argparse.ArgumentParser(description='Paper Manager')
    parser.add_argument('command', type=str, nargs=1, help='execute one of the commands:\n\tadd\n\tlist\n\tupdate\n\topen\n\tindex\n\tremove')
    args = parser.parse_args(sys.argv[1:2])
    #print args.command
    cmd = args.command[0]
    if   cmd == 'add':
        run_add_paper()
    elif cmd == 'list':
        run_search()
    elif cmd == 'update':
        run_update()
    elif cmd == 'index':
        db.index(indexAll=True)
    elif cmd=='open':
        for paper_id in sys.argv[2:]:
            if paper_id in db.entries:
                paper_path, _ = db.entries[paper_id]
                call(['gvfs-open', paper_path])
    elif cmd=='remove':
        for paper_id in sys.argv[2:]:
            db.remove(paper_id)
        db.persist()
