

import sys
import os
import shutil
import tempfile

from subprocess import call

import argparse
import configparser

from paper import *
from paperbase import *

import indexer

db = None

def prompt_editor(file_path):
    EDITOR = os.environ.get('EDITOR','vim') #that easy!
    initial_text = '' # if you want to set up the file somehow
    if os.path.isfile(file_path):
        with open(file_path) as f:
            initial_text = f.read()
    call([EDITOR, file_path])

def read_from_editor():
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
        paper = db.insert(args.paper_file[0],args.bibtex_file[0])
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

def run_search():
    print db.entries
    parser = argparse.ArgumentParser(description='Paper Manager [search]')
    #search/list command
    parser.add_argument('--list-tags', nargs='?', const=True, default=False, help='List all known tags')
    parser.add_argument('--words', metavar='<word>', type=str, nargs='+',
                          help='individual words to search for')
    parser.add_argument('--tags', metavar='<tag>', type=str, nargs='+',
                          help='a list of comma separated tags to search for')
    parser.add_argument('--years', metavar='<year>', type=str, nargs='+',
                          help='filter for specific years')
    parser.add_argument('--authors', metavar='<author>', type=str, nargs='+',
                          help='a list of comma separated authors to search for')



if __name__=='__main__':
    base_path = os.environ.get('HOME','.')+'/.paperman'
    db = PaperBase(base_path)
    #print sys.argv
    parser = argparse.ArgumentParser(description='Paper Manager')
    parser.add_argument('command', type=str, nargs=1, help='execute one of the commands: add, search, or update')
    args = parser.parse_args(sys.argv[1:2])
    #print args.command
    cmd = args.command[0]
    if   cmd == 'add':
        run_add_paper()
    elif cmd == 'search':
        run_search()
