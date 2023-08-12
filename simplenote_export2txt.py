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
import email.utils
import json
import os
import string
import sys
import time
from zipfile import ZipFile, ZIP_DEFLATED

is_win = sys.platform.startswith('win')

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
    if is_win:
        # TODO log warning
        print('WARNING Windows, but missing pywin32, unable to set file creation time')


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

def dict2txt(notes_dict, output_directory='notes_export_dir', use_first_line_as_filename=False, file_extension='txt', save_index=True):
    #import pdb ; pdb.set_trace()
    dupe_dict = sanity_check_export.find_duplicate_filenames_dict(notes_dict, generate_file_name=sanity_check_export.safe_filename)
    if save_index:
        new_index = {
            'trashedNotes': notes_dict['trashedNotes'],  # include trashed/deleted notes (for now), including actual content  # TODO make optional
            'activeNotes': {},  # this will be the note metadata without the content (and additional "filename")
        }

    safe_mkdir(output_directory)
    notes = {}
    for note_entry in notes_dict['activeNotes']:
        # handle platform format differences with newlines/linefeeds
        note_entry['content'] = note_entry['content'].replace('\r', '')  # I don't use an Apple Mac, I've no idea if this will break OS X - works for Windows, Linux, and Android
        filename = note_entry['id']
        first_line = note_entry['content'].split('\n', 1)[0]
        safe_filename = sanity_check_export.safe_filename(first_line)
        if safe_filename.lower() in dupe_dict:
            safe_filename = 'dupe__' + safe_filename.lower() + '__' + note_entry['id']  # TODO review if should use lower in generated final name for dupes?
        if use_first_line_as_filename:
            filename = safe_filename

        # TODO check for markdown and potentially change/set file_extension?
        if file_extension:
            filename = filename + '.' + file_extension
        filename = os.path.join(output_directory, filename)
        st_atime = time.time()  # current time for; Time of most recent access expressed in seconds.
        st_mtime = iso_like2secs(note_entry['lastModified'])  # Time of most recent content modification expressed in seconds.
        if windows_set_create_time:
            created_time = iso_like2secs(note_entry['creationDate'])
        f = open(filename, 'wb')
        f.write(note_entry['content'].encode('utf-8'))
        f.close()
        # modify file timestamp(s)
        os.utime(filename, (st_atime, st_mtime))
        if windows_set_create_time:
            #
            windows_set_create_time(filename, created_time)
        if save_index:
            del note_entry['content']
            note_entry['filename'] = safe_filename
            new_index['activeNotes'][note_entry['id']] = note_entry
    if save_index:
        filename = os.path.join(output_directory, 'simplenote_index.json')
        f = open(filename, 'wb')
        f.write(json.dumps(new_index, indent=1).encode('utf-8'))  # small indent for debugging purposes
        f.close()


def main(argv=None):
    if argv is None:
        argv = sys.argv

    # FIXME proper command line argument processing needed
    filename = ''
    filename = argv[1]
    try:
        use_first_line_as_filename = argv[2]
        use_first_line_as_filename = True
    except IndexError:
        use_first_line_as_filename = False

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
    dict2txt(notes_dict, output_directory=filename+'_dir', use_first_line_as_filename=use_first_line_as_filename)


    return 0


if __name__ == "__main__":
    sys.exit(main())
