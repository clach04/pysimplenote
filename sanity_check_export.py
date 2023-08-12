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


def report_on_dupes(filename_dict):
    for filename in filename_dict:
        if len(filename_dict[filename]) > 1:
            print('dupe %r x%d - %r' % (filename, len(filename_dict[filename]), filename_dict[filename]))

def check_notes_zip(archname, simulate=True):
    assert simulate
    filenames = {}
    arch = ZipFile(archname, 'r')
    for orig_path in arch.namelist():
        filename = orig_path.lower()
        id_list = filenames.get(filename, [])
        if id_list:
            print('found a duplicate: lower: %r - %r and %r' % (filename, orig_path, filenames[filename]))
        id_list.append((orig_path, ))
        filenames[filename] = id_list


    print('*' * 34)
    report_on_dupes(filenames)

def check_json_entries(archname, simulate=True):
    assert simulate
    #import pdb ; pdb.set_trace()
    arch = ZipFile(archname, 'r')
    f = arch.open('source/notes.json')
    json_bytes = f.read()
    f.close()
    notes_dict = json.loads(json_bytes)
    check_notes_dict(notes_dict)

def safe_filename(filename, replacement_char='_', max_filename_length=100):
    """safe filename for almost any platform, NOTE filename NOT pathname
    does NOT handle paths, see blocked_filenames comments section below for details/example.
    aka slugify()
    # TODO max filename truncation?
    """
    result = []
    last_char = ''
    for x in filename:
        if not(x.isalnum() or x in '-_'):
            x = replacement_char
        if x not in ['-', replacement_char] or last_char not in ['-', replacement_char]:
            # avoid duplicate '_'
            result.append(x)
        last_char = x

    new_filename = ''.join(result)
    """now prefix _ infront of special names, mostly impacts Windows.
    For example handle this sort of mess:

        C:\tmp>echo hello > con.txt
        hello

        C:\tmp>echo hello > \tmp\con.txt
        hello

        C:\tmp>echo hello > C:\tmp\con.txt
        hello

        C:\tmp>echo hello > C:\tmp\_con.txt
        C:\tmp>echo hello > C:\tmp\con_.txt

    Doc refs:
    * https://en.wikipedia.org/wiki/Filename#In_Windows
    * https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file?redirectedfrom=MSDN
        blocked_filenames = 'CON, PRN, AUX, NUL, COM0, COM1, COM2, COM3, COM4, COM5, COM6, COM7, COM8, COM9, LPT0, LPT1, LPT2, LPT3, LPT4, LPT5, LPT6, LPT7, LPT8, LPT9'
        and NULL for good measure

    """
    blocked_filenames = [
        'CON',
        'PRN',
        'AUX',
        'NUL',
        'NULL',  # redundant but here for saftey incase approach changes
        'COM0',
        'COM1',
        'COM2',
        'COM3',
        'COM4',
        'COM5',
        'COM6',
        'COM7',
        'COM8',
        'COM9',
        'LPT0',
        'LPT1',
        'LPT2',
        'LPT3',
        'LPT4',
        'LPT5',
        'LPT6',
        'LPT7',
        'LPT8',
        'LPT9'
        ]
    new_filename_upper = new_filename.upper()
    for device_name in blocked_filenames:
        """
        if new_filename_upper.startswith(device_name):
            new_filename = '_' + new_filename
            break
        """
        #if new_filename_upper == device_name or new_filename_upper.startswith(device_name + '.'):
        # postfix an underscore/bar '_'  # TODO use double do help id possible problem filenames?
        if new_filename_upper == device_name:
            new_filename = new_filename + '_'
            break
        elif new_filename_upper.startswith(device_name + '.'):
            new_filename = new_filename[:len(device_name)] + '_' +new_filename[len(device_name):]
            break


    if new_filename == '':
        new_filename = 'unname_file'

    if max_filename_length:
        if len(new_filename) > max_filename_length:
            new_filename = new_filename[:max_filename_length-2] + '__'  # append multiple '__' to indicate may want review

    return new_filename


def find_duplicate_filenames_dict(notes_dict, generate_file_name=None, remove_unique_names_from_results=True):
    """also see check_notes_dict() and report_on_dupes()
    generate_file_name parameter can be used with safe_filename()
    """
    # check each note
    filenames = {}
    for note_entry in notes_dict['activeNotes']:
        #print('%r' % note_entry)
        #print('%s' % json.dumps(note_entry, indent=4))
        content = note_entry['content']  # under Android content will only have '\n', Windows Native Application (and Windows browser) will have '\r' as well)
        content = content.replace('\r', '')  # I don't use a Mac, I've no idea if this will break Mac
        first_line = content.split('\n', 1)[0]
        #print('%r' % first_line)
        filename = first_line
        if generate_file_name:
            filename = generate_file_name(first_line)
        filename_lower = filename.lower()
        # TODO safe filename
        id_list = filenames.get(filename_lower, [])
        id_list.append((filename, note_entry['id']))
        filenames[filename_lower] = id_list
    # TODO remove non-duplicate entries?
    if remove_unique_names_from_results:
        for filename in list(filenames.keys()):
            if len(filenames[filename]) == 1:
                del filenames[filename]

    return filenames


def check_notes_dict(notes_dict):
    # also see find_duplicate_filenames_dict() and report_on_dupes()
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
        #'tags',  # list/array of strings
    ]
    if 'markdown' in note_keys:
        note_keys_expected.append('markdown')
    if 'tags' in note_keys:
        note_keys_expected.append('tags')
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
    print('*' * 34)
    report_on_dupes(filenames)



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
        print('json dupe check')
        print('-' * 65)
        dupe_dict = find_duplicate_filenames_dict(notes_dict)
        print('json dupe check report')
        print('-' * 65)
        report_on_dupes(dupe_dict)
        print('json dupe check - safe filenames')
        print('-' * 65)
        dupe_dict = find_duplicate_filenames_dict(notes_dict, generate_file_name=safe_filename)
        print('json dupe check report')
        print('-' * 65)
        report_on_dupes(dupe_dict)

    return 0


if __name__ == "__main__":
    sys.exit(main())
