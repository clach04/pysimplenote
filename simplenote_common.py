#!/usr/bin/env python
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
#
# Utility functions for SimpleNote json export files
# Copyright (C) 2024 Chris Clark - clach04

import email.utils
import datetime
import json
import os
import string
import sys
from zipfile import ZipFile, ZIP_DEFLATED


is_win = sys.platform.startswith('win')

def safe_mkdir(newdir):
    result_dir = os.path.abspath(newdir)
    try:
        os.makedirs(result_dir)
    except OSError as info:
        if info.errno == 17 and os.path.isdir(result_dir):
            pass
        else:
            raise

def iso_like2datetime_local(datetime_str):
    """Partial ISO date format parsing, very limited.
    Focused on Simplenote timestamps format which are UTC / Zulu / GMT0 based.
    For example; "2022-06-27T01:39:12.602Z" and "2012-02-22T15:15:19.602Z"
    Returns relative to local timezone (what ever that maybe), no support for other timezones
    """
    assert datetime_str.endswith('Z')  # FIXME add a check, this can be optimized out
    datetime_str = datetime_str[:-1]  # strip UTC indicator
    d = datetime.datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%f')  # UTC relative datetime
    # generate tuple like the one returned by email.utils.parsedate_tz()
    # Daylight Saving Time flag is set to -1, since DST is unknown.
    dst = -1
    tz_offset = 0
    date_tuple = d.year, d.month, d.day, d.hour, d.minute, d.second, d.microsecond, 1, dst,tz_offset  # UTC offset
    utctimestamp = email.utils.mktime_tz(date_tuple)
    return datetime.datetime.fromtimestamp(utctimestamp)

def iso_like2secs(datetime_str):
    """Partial ISO date format parsing, very limited.
    Focused on Simplenote timestamps format which are UTC / Zulu / GMT0 based.
    For example; "2022-06-27T01:39:12.602Z" and "2012-02-22T15:15:19.602Z"
    """
    assert datetime_str.endswith('Z')  # FIXME add a check, this can be optimized out
    datetime_str = datetime_str[:-1]  # strip UTC indicator
    d = datetime.datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%f')  # UTC relative datetime
    # generate tuple like the one returned by email.utils.parsedate_tz()
    date_tuple = d.year, d.month, d.day, d.hour, d.minute, d.second, d.microsecond, 1, -1, 0  # UTC offset
    utctimestamp = email.utils.mktime_tz(date_tuple)
    return utctimestamp

def force_bool(in_bool):
    """Force string value into a Python boolean value
    Everything is True with the exception of; false, off, no, and 0"""
    value = str(in_bool).lower()
    if value in ('false', 'off', 'no', '0'):
        return False
    else:
        return True


def load_file(filename):
    """zip with json (*.txt files are IGNORED) or plain json

    Expect a schema like:
        {
          "activeNotes": [
            {
              "id": "206549e6-2fcc-4b79-b58e-44d758623cfa",
              "content": "simplenote todo note 2024-03-18\r\n\r\n\r\nthere are now dupes in here due to new UUID on import.\r\nnotes renamed radically so not planning on mergeing\r\n\r\nTODO trash all notes (put UUID into trash) and re-import?\r\ndo not want to have to delete account. See (no progress) https://github.com/Automattic/simplenote-electron/issues/3114\r\nand also see https://fletcherpenney.net/2010/01/how_to_delete_all_notes_from_simple\r\nhttps://fletcherpenney.net/other_projects/simplenotesync/\r\nhttps://github.com/fletcher/SimplenoteSync\r\nhttps://github.com/fletcher/SimplenoteSync/blob/master/nuclear-option.pl\r\n",
              "creationDate": "2024-03-19T05:03:04.477Z",
              "lastModified": "2024-03-19T15:49:29.254Z",
              "markdown": true,
              "pinned": true,
              "tags": [
                  "tag"
              ]
            }
          ],
          "trashedNotes": [
            {...}
            ]
        }
    NOTES
      * simplenote.com max file limit for import is 5MB
      * looks like newlines for content are Windows (simplenote.com seems to accept unix)
      * id/uuid may or maynot have "-" character, but tends to have it (very old entries do not)
          * on import UUID ignored and likely to be replaced by simplenote.com
    """
    if filename.lower().endswith('.json'):
        print('Extracting from Simplenote raw json file')
        print('-' * 65)
        f = open(filename, 'rb')
        json_bytes = f.read()
        f.close()
        notes_dict = json.loads(json_bytes)
    else:
        # assume a zip file
        print('Extracting from Simplenote json in zip')
        print('-' * 65)
        arch = ZipFile(filename, 'r')
        f = arch.open('source/notes.json')
        json_bytes = f.read()
        f.close()
        notes_dict = json.loads(json_bytes)
    return notes_dict

def export_to_uuid_dict(notes_dict):
    """take output from load_file() and generate a dictionary where key is id/uuid mapping to note dictionary (including (duplicate) id)
    Ignores trash
    """
    result = {}
    for entry in notes_dict["activeNotes"]:
        result[entry["id"].replace('-', '')] = entry
    return result
