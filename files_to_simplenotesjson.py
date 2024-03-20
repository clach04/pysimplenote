#!/usr/bin/env python
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
#
"""Generate SimpleNote json file for import from *.md and *.txt files

NOTE only does current directory, not nested/sub-directories
Doees not handle git repos with deleted files.
"""

import datetime
import glob
import fnmatch
import json
import os
import string
import sys
import time
import uuid


is_py3 = sys.version_info >= (3,)
is_win = sys.platform.startswith('win')
extensions_to_check = ['.md', '.txt']  # NOTE case sensitive  # TODO consuder using fnmatch and case insensitive

def pattern_to_file_list(pattern):
    filenames = []
    for filename_pattern in extensions_to_check:
        filenames += glob.glob(pattern + filename_pattern)
    return filenames


def filename_to_entry(filename):
    ctime = os.path.getctime(filename)
    mtime = os.path.getmtime(filename)
    # string in ISO format without micro/milli-secs and Z
    #time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime('.bashrc')))  # local time
    #time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(os.path.getmtime('.bashrc')))  # UTC / GMT
    #
    # datetime
    #datetime.datetime.fromtimestamp(os.path.getmtime('.bashrc'))  # local

    f = open(filename, 'rb')
    binary_data = f.read()
    f.close()
    note_content = binary_data.decode('utf-8')  # TODO other encoding options
    # TODO newline translation needed here? expected to be Windows "\r\n". Simplenote.com seems to accept Unix newlines.
 
    result = {
      "id": "%s" % uuid.uuid4(),  # 32-byte UUID, with or without hypens/dashes - could use md5sum
      "content": note_content,
      "creationDate": time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime(mtime)),  # TODO non-fake sub-seconds  # UTC / GMT  - example: "2022-06-25T19:32:18.000Z",
      "lastModified": time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime(ctime)),
      #"markdown": true
      # tags?
    }
    return result


filenames = pattern_to_file_list('*')

now = datetime.datetime.now()
output_filename = os.environ.get('SIMPLENOTE_EXPORT_FILENAME', 'simplenote_%s.json' % now.strftime('%Y%m%d_%H%M%S'))
print('%d files to export' % len(filenames))
print('to export %r' % output_filename)
notes = []
for filename in filenames:
    print('%s' % filename)
    notes.append(filename_to_entry(filename))

simplenotes_dict = {
    "activeNotes": notes,
    "trashedNotes": [],  # NOTE required, web interface will silently crash if missing (error in debug console, but nothing in UI).
}

json_str = json.dumps(simplenotes_dict, indent=4)
#print('%s' % json_str)
#"""
f = open(output_filename, 'wb')
f.write(json_str.encode('utf-8'))
f.close()
#"""
