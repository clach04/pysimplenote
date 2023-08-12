# pysimplenote

Home page https://github.com/clach04/pysimplenote

Python tools / library for working with Simplenote by Automattic

Tools for working with:

  * https://en.wikipedia.org/wiki/Simplenote
  * https://simplenote.com/

Python 3 or 2.

Works with either json files or zip export/backup files (NOTE actually uses the json file in the zip and ignores the text files).

## Getting Started

  * Most of the tools work with the standard Python library, e.g. sanity_check_export
      * simplenote_export2txt can optionally under Windows use the pywin32 extensions from https://github.com/mhammond/pywin32 to set creation date/time
  * simplenote_json2yaml **requires** additional lib, pyyaml

## Tools

### sanity_check_export

Look for duplicate titles/filenames and notes that are missing (or have suspicious) titles/filenames (only one line, with no body text).
Real duplicates or under Microsoft Windows file system allows case for display but is caseless when it compares to storage, for example, `music` versus `Music`)

Checks:

  * filenames in zip
  * entries in json in both raw json and zip

### simplenote_export2txt

Convert json export to text files for easier diff/sync with traditional file based tools

Setting the last modified timestamp metadata correctly, and optionally under Windows setting creation timestamp.

Possible use cases:

  * view, print, or even edit in plain text editor
  * synchronize to another filesystem/backend - for example; rsync, FreeFileSync, JSync, rclone, GDrive, OneDrive, ownCloud, Nextcloud, etc.
  * perform diff across different backups/exports - for example; `diff -r`, WinMerge, Meld, etc.
  * find possible problem notes (duplicate titles/first lines and/or long/single-line notes)

Under windows install pywin32

    python -m pip install pywin32 --upgrade

Example Usage:

    python simplenote_json2yaml.py note.zip
    python simplenote_json2yaml.py note.zip use_first_line_as_filename

    python simplenote_json2yaml.py simplenote.json
    python simplenote_json2yaml.py simplenote.json use_first_line_as_filename

Then look for problem filenames:

  * `ls *__*` - find duplicate filenams (also `ls dupe__*`)
  * `ls *_.txt` - find truncated/long titles and/or trailing blanks

### simplenote_json2yaml

Convert/export json file to yaml with indents, sorted on id. Requires pyyaml:

    pip install pyyaml==3.12

Allows single file diff.

## Similar/related tools

  * https://github.com/siviae/gitjournal-simplenote-exporter
    NOTE expects zip files ONLY (not json, like from Android).
    Problems:
      * does not generate safe filenames (e.g. `/`)
