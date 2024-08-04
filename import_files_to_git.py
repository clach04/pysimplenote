#!/usr/bin/env python
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
#
# For each *.txt file in single/flat directory create git add/commit script that uses the file last modified date/time to commit to a git repo (in time order)
# All commits are for a single file (not grouped)
# Also see related script simplenote_export2txt.py, which exports from a simplenote export directly into a (new) git repo, with timestamps using Dulwich (git implementation)
# Copyright (C) 2023 Chris Clark - clach04

import datetime
import json
import glob
import os
import string
import sys

is_win = sys.platform.startswith('win')

CREATED = 'CREATED'
MODIFIED = 'MODIFIED'

def main(argv=None):
    if argv is None:
        argv = sys.argv
    comment_prefix = '#'
    if is_win:
        comment_prefix = 'REM'
    print('%s Python %s on %s' % (comment_prefix, sys.version.replace('\n', ' '), sys.platform.replace('\n', ' ')))
    filename_list = glob.glob('*.txt')
    times_and_filenames = []
    for filename in filename_list:
        #print('%r' % filename)
        fd = os.open(filename, os.O_RDONLY)
        file_status = os.fstat(fd)
        os.close(fd)
        # TODO add user controlled option to disable creation/modification detection (for Unix/Linux use cases)
        created_modified_times = [file_status.st_ctime, file_status.st_mtime]  # Under Microsoft Windows st_ctime is create time, Unix it is the time of the last metadata change
        created_modified_times.sort()
        st_ctime, st_mtime = created_modified_times
        times_and_filenames.append((st_ctime, filename, CREATED))
        if st_ctime != st_mtime:
            times_and_filenames.append((st_mtime, filename, MODIFIED))

    times_and_filenames.sort()  # sort by timestamp
    #print('%s' % json.dumps(times_and_filenames, indent=4))  # DEBUG
    # Generate shell / batch script to stdout - assume now unicode filenames for Windows
    print('git init')
    for timestamp, filename, file_op in times_and_filenames:
        print('%s %s' % (comment_prefix, datetime.datetime.fromtimestamp(timestamp)))
        if '"' in filename:
            raise NotImplementedError('Double quotes in filenames, %r' % filename)
        """
        if file_op == MODIFIED:
            # file was modified (at least once) since creation, want to reflect that in git history but have no way to reflect that (built-in to git)
            # Options:
            # 1. --allow-empty flag to commit
            # 2. delete and re-add
            # 3. https://github.com/przemoc/metastore - NOTE no create time support (as that's a Windows concept, not Unix)
            # 4. https://gist.github.com/andris9/1978266 - NOTE no create time support (as that's a Windows concept, not Unix)
        """
        # Use --allow-empty for potentially unchanged files (the add is going to essentially be ignored by git)
        # NOTE "git log" will show this, BUT "git log FILENAME" will only show the real changes (i.e. initial)
        command_str = '''git add "%s"
git commit --allow-empty -m "%s %s" --date=%d "%s"
'''
        print(command_str % (filename, file_op, filename, timestamp, filename))
        # TODO add error checking to output script (this would be platform specific though...)

    return 0


if __name__ == "__main__":
    sys.exit(main())
