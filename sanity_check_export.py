#!/usr/bin/env python
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
#
# Find potentially problems in Simplenote export file
# Copyright (C) 2023 Chris Clark - clach04
"""Handles ZIP and json only exports

Find problems:

  * duplicate filename
  * missing newline(s)

given zip file which is SimpleNote export (from the web version of Simplenote - https://simplenote.com/help/#export), locate duplicate notes/filenames.

Reasons duplicates can occur in SimpleNote:

  * mixed case, under Windows file system records case BUT treats as caseless
    For example; Music.txt, MUSIC.txt, and music.txt

NOTE as of 2023-08-09 Android application only exports json file.

NOTE ZIP export uses first line of note as filename, which may not be a valid filename for your platform.

"""

import json
import os
import string
import sys
from zipfile import ZipFile, ZIP_DEFLATED


def check_notes_zip(archname, simulate=True):
    assert simulate
    filenames = {}
    arch = ZipFile(archname, 'r')
    for orig_path in arch.namelist():
        filename = orig_path.lower()
        if filenames.get(filename):
            print('found a duplicate: lower: %r - %r and %r' % (filename, orig_path, filenames[filename]))
        else:
            filenames[filename] = orig_path


def check_json_entries(archname, simulate=True):
    assert simulate
    #import pdb ; pdb.set_trace()
    arch = ZipFile(archname, 'r')
    f = arch.open('source/notes.json')
    json_bytes = f.read()
    f.close()
    notes_dict = json.loads(json_bytes)
    check_notes_dict(notes_dict)

def check_notes_dict(notes_dict):
    top_level_keys = list(notes_dict.keys())
    top_level_keys.sort()
    top_level_keys_expected = [u'activeNotes', u'trashedNotes',]
    top_level_keys_expected.sort()
    print(top_level_keys)
    assert top_level_keys == top_level_keys_expected
    note_keys = list(notes_dict['activeNotes'][0].keys())
    note_keys.sort()
    note_keys_expected = [
        'id',  # string - appears to be UUID (UUID4?)
        'content',  # string
        'creationDate',  # ISO/ANSI format string UTC
        'lastModified',  # ISO/ANSI format string UTC
        #'markdown',  # Boolean - NOTE optional?
    ]
    if 'markdown' in note_keys:
        note_keys_expected.append('markdown')
    note_keys_expected.sort()
    assert note_keys_expected == note_keys, (note_keys_expected, note_keys)

    # check each note
    filenames = {}
    for note_entry in notes_dict['activeNotes']:
        #print('%r' % note_entry)
        #print('%s' % json.dumps(note_entry, indent=4))
        content = note_entry['content']  # under Android content will only have '\n', Windows Native Application (and Windows browser) will have '\r' as well)
        content = content.replace('\r', '')  # I don't use a Mac, I've no idea if this will break Mac
        """
        location_linefeed = content.find('\r')
        location_newline = content.find('\n')
        #assert -1 not in (location_linefeed, location_newline), (location_linefeed, location_newline, note_entry['id'], content[:100])
        if -1  in (location_linefeed, location_newline):
            print('missing newline/linefeed in content for %r' % ((location_linefeed, location_newline, note_entry['id'], content[:100]),))
        orig_path = content.split('\r', 1)[0]  # TODO clean up \r and \n incase of problems?
        """
        location_newline = content.find('\n')
        if -1 == location_newline:
            print('missing newline in content for %r' % ((location_newline, note_entry['id'], content[:100]),))
            #orig_path = content.split('\n', 1)[0]
            #print('\t%r' % orig_path)
        orig_path = content.split('\n', 1)[0]
        #print('%r' % orig_path)
        filename = orig_path.lower()
        id_list = filenames.get(filename, [])
        if id_list:
            print('found a duplicate: lower: %r - %r and %r' % (filename, orig_path, filenames[filename]))
        id_list.append((orig_path, note_entry['id']))
        filenames[filename] = id_list



def main(argv=None):
    if argv is None:
        argv = sys.argv

    filename = ''
    filename = argv[1]

    simulate = True
    if filename.lower().endswith('.zip'):
        print('Checking text files in zip')
        print('-' * 65)
        check_notes_zip(filename, simulate)
        print('-' * 65)
        print('Checking json')
        print('-' * 65)
        check_json_entries(filename, simulate)
    else:
        # lets assumes it is a json file
        print('Checking json ONLY')
        print('-' * 65)
        f = open(filename, 'rb')
        json_bytes = f.read()
        f.close()
        notes_dict = json.loads(json_bytes)
        check_notes_dict(notes_dict)

    return 0


if __name__ == "__main__":
    sys.exit(main())
