#!/usr/bin/env python
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
#
# Convert json export to (id sorted) YAML for easier diffing
# Copyright (C) 2023 Chris Clark - clach04

import json
import os
import string
import sys
from zipfile import ZipFile, ZIP_DEFLATED

import yaml  # pip install pyyaml==3.12  (for python2 and 3 support - TODO requirements.txt)


def dict2yaml(notes_dict, filename='debug.yaml'):
    notes = {}
    for note_entry in notes_dict['activeNotes']:
        note_entry['content'] = note_entry['content'].replace('\r', '')  # I don't use a Mac, I've no idea if this will break Mac
        notes[note_entry['id']] = note_entry
    f = open(filename, 'wb')
    yaml_str = yaml.safe_dump(notes, default_flow_style=False)  # keys will be sorted
    f.write(yaml_str)
    f.close()

    """
    filename = 'debug.json'
    f = open(filename, 'wb')
    f.write(json.dumps(notes, indent=4))
    f.close()
    """


def main(argv=None):
    if argv is None:
        argv = sys.argv

    filename = ''
    filename = argv[1]

    if filename.lower().endswith('.json'):
        print('Checking json ONLY')
        print('-' * 65)
        f = open(filename, 'rb')
        json_bytes = f.read()
        f.close()
        notes_dict = json.loads(json_bytes)
    else:
        # assume a zip file
        print('Checking json in zip')
        print('-' * 65)
        arch = ZipFile(filename, 'r')
        f = arch.open('source/notes.json')
        json_bytes = f.read()
        f.close()
        notes_dict = json.loads(json_bytes)
    dict2yaml(notes_dict, filename=filename+'.yaml')


    return 0


if __name__ == "__main__":
    sys.exit(main())
