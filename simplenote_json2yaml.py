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

import yaml


def dict2yaml(notes_dict):
    notes = {}
    for note_entry in notes_dict['activeNotes']
        notes[note_entry['id']] = note_entry
    filename = 'debug.yaml'
    f = open(filename, 'wb')
    yaml_str = yaml.dump(notes)
    f.write(yaml_str)
    f.close()


def main(argv=None):
    if argv is None:
        argv = sys.argv

    filename = ''
    filename = argv[1]


    return 0


if __name__ == "__main__":
    sys.exit(main())
