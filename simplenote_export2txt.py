#!/usr/bin/env python
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
#
# Convert json export to text files for easier diff/sync with traditional file based tools
# Copyright (C) 2023 Chris Clark - clach04
"""Only dumps active notes, not trashed/deleted notes

Can:

  * uses id as filename to avoid duplicates and potentially invalid names (too long, unsupported characters, etc.).
  * use first line of note as filename, note file name will be cleaned/filtered/made-safe

Possible future TODO items:

  * if markdown flag true, save with .md extension?

"""

import datetime
import json
import os
import string
import sys
import time
from zipfile import ZipFile, ZIP_DEFLATED


try:
    #python -m pip install pywin32 --upgrade
    import pywintypes
    import win32con
    import win32file
    # Alternatively checkout:
    #   * https://github.com/Delgan/win32-setctime BUT requires Python 3.5+
    #   * https://github.com/kubinka0505/filedate BUT requires Python 3.4+

    def windows_set_create_time(fname, newtime):
        wintime = pywintypes.Time(newtime)
        winfile = win32file.CreateFile(
            fname, win32con.GENERIC_WRITE,
            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
            None, win32con.OPEN_EXISTING,
            win32con.FILE_ATTRIBUTE_NORMAL, None)

        win32file.SetFileTime(winfile, wintime, None, None)

        winfile.close()
except ImportError:
    # Either not Windows or missing extensions
    windows_set_create_time = None


import sanity_check_export


def safe_mkdir(newdir):
    result_dir = os.path.abspath(newdir)
    try:
        os.makedirs(result_dir)
    except OSError as info:
        if info.errno == 17 and os.path.isdir(result_dir):
            pass
        else:
            raise

def iso_like2datetime(datetime_str):
    """Partial ISO date format parsing, very limited.
    Focused on Simplenote timestamps format which are UTC / Zulu / GMT0 based
    """
    datetime_str = datetime_str.split('.', 1)[0]  # strip fractional seconds and UTC indicator
    return datetime.datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S')

def dict2txt(notes_dict, output_directory='notes_export_dir', use_first_line_as_filename=False, file_extension='txt'):
    #import pdb ; pdb.set_trace()
    if use_first_line_as_filename:
        dupe_dict = sanity_check_export.find_duplicate_filenames_dict(notes_dict, generate_file_name=sanity_check_export.safe_filename)

    safe_mkdir(output_directory)
    notes = {}
    for note_entry in notes_dict['activeNotes']:
        # handle platform format differences with newlines/linefeeds
        note_entry['content'] = note_entry['content'].replace('\r', '')  # I don't use an Apple Mac, I've no idea if this will break OS X - works for Windows, Linux, and Android
        filename = note_entry['id']
        if use_first_line_as_filename:
            first_line = note_entry['content'].split('\n', 1)[0]
            filename = sanity_check_export.safe_filename(first_line)
            if filename.lower() in dupe_dict:
                filename = 'dupe__' + filename.lower() + '__' + note_entry['id']  # TODO review if should use lower in generated final name for dupes?

        # TODO check for markdown and potentially change/set file_extension?
        if file_extension:
            filename = filename + '.' + file_extension
        filename = os.path.join(output_directory, filename)
        st_atime = time.time()  # current time for; Time of most recent access expressed in seconds.
        last_modified = iso_like2datetime(note_entry['lastModified'])
        st_mtime = time.mktime(last_modified.timetuple())  # Time of most recent content modification expressed in seconds.
        if windows_set_create_time:
            created_time = iso_like2datetime(note_entry['creationDate'])
        f = open(filename, 'wb')
        f.write(note_entry['content'].encode('utf-8'))
        f.close()
        # modify file timestamp(s)
        os.utime(filename, (st_atime, st_mtime))
        if windows_set_create_time:
            windows_set_create_time(filename, created_time)


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
    dict2txt(notes_dict, output_directory=filename+'_dir', use_first_line_as_filename=True)


    return 0


if __name__ == "__main__":
    sys.exit(main())
