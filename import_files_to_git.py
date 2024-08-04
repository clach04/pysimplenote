#!/usr/bin/env python
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
#
# For each *.txt file in single/flat directory create git add/commit script that uses the file last modified date/time to commit to a git repo (in time order)
# Also see related script simplenote_export2txt.py, which exports from a simplenote export directly into a (new) git repo, with timestamps using Dulwich (git implementation)
# Copyright (C) 2023 Chris Clark - clach04

import datetime
import json
import glob
import os
import string
import sys


def main(argv=None):
    if argv is None:
        argv = sys.argv
    print('# Python %s on %s' % (sys.version.replace('\n', ' '), sys.platform.replace('\n', ' ')))
    filename_list = glob.glob('*.txt')
    times_and_filenames = []
    for filename in filename_list:
        #print('%r' % filename)
        fd = os.open(filename, os.O_RDONLY)
        file_status = os.fstat(fd)
        os.close(fd)
        times_and_filenames.append((file_status.st_mtime, filename, ))

    times_and_filenames.sort()  # sort by timestamp
    #print('%s' % json.dumps(times_and_filenames, indent=4))  # DEBUG
    # Generate shell / batch script to stdout - assume now unicode filenames for Windows
    print('git init')
    for timestamp, filename in times_and_filenames:
        command_str = '''git add "%s"
git commit -m "%s" --date=%d
'''
        print(command_str % (filename, filename, timestamp))

    return 0


if __name__ == "__main__":
    sys.exit(main())
