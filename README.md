# pysimplenote

Home page https://github.com/clach04/pysimplenote

Python tools / library for working with Automattic's Simplenote.

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

Under windows install pywin32 to preserve file creation date

    python -m pip install pywin32 --upgrade

Install Dulwich (git is NOT required) if exporting history to git:

    pip install dulwich==0.19.16 --global-option="--pure"

Example Usage:

    python simplenote_json2yaml.py note.zip
    python simplenote_json2yaml.py note.zip use_first_line_as_filename

    python simplenote_json2yaml.py simplenote.json
    python simplenote_json2yaml.py simplenote.json use_first_line_as_filename

Alternative options via operating system environment variables:

        export SIMPLENOTE_READABLE_FILENAMES=true
        # recommend using import_files_to_git.py and leave false/unset
        export SIMPLENOTE_USE_GIT=true

        env SIMPLENOTE_READABLE_FILENAMES=true SIMPLENOTE_USE_GIT=true python simplenote_export2txt.py export_filename

        set SIMPLENOTE_READABLE_FILENAMES=true
        :: recommend using import_files_to_git.py and leave false/unset
        set SIMPLENOTE_USE_GIT=true

Then look for problem filenames:

  * `ls *__*` - find duplicate filenams (also `ls dupe__*`)
  * `ls *_.txt` - find truncated/long titles and/or trailing blanks

#### Git notes

##### Speed and sort order

Git support is via Dulwich and is not super fast, also the initial repo will be large.
Example, 3.2M json file, ends up as git repo + checkout of 48M. This repo pushed to a modern git server and re-cloned will be 8.6M as repo+checkout.

On one machine same json file:
  * plain text extract takes 0.6 seconds to extract
  * with Dulwich git enabled takes 6 mins and 17 seconds.
  * Same git import with git command line tool takes 37 seconds, repo+checkout is 49M.

ALSO NOTE commit order is in file order (in json file), not last modified orded.

Alternative, disable git support and use `import_files_to_git.py` to generate a script that will create the git repo with correct order (which tools like GitJournal expect).

##### gitignore

Recommend creating a `.gitignore` file, contents something like:

    *.bak
    *~

##### File mtime / last modified date / timestamp

`git-restore-mtime` from https://github.com/MestreLion/git-tools is a Python3 script that can restore last modified (commit) times to files on file system.


### simplenote_json2yaml

Convert/export json file to yaml with indents, sorted on id. Requires pyyaml:

    pip install pyyaml==3.12

Allows single file diff.

### files_to_simplenotesjson

Generate a json file to be imported into SimpleNote based on directory of *.txt and *.md files in the current directory.

  * expects each file to be utf8 encoded
  * no (nested) subdirectories

Usage:

    # set OS var SIMPLENOTE_EXPORT_FILENAME to output filename, defaults to simplenote_CURRENT_TIMESTAMP.json
    python files_to_simplenotesjson.py

Example Unix/Linux:

    env SIMPLENOTE_EXPORT_FILENAME=/tmp/simplenote.json python files_to_simplenotesjson.py

## Future / TODO ideas

  * https://github.com/clach04/pysimplenote/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement


## Similar/related tools

  * https://github.com/siviae/gitjournal-simplenote-exporter
    NOTE expects zip files ONLY (not json, like from Android).
    Problems:
      * does not generate safe filenames (e.g. `/`) https://github.com/siviae/gitjournal-simplenote-exporter/issues/3
   
  * https://github.com/clach04/quillpad_conversion for [Quillpad](https://github.com/quillpad/quillpad) (nee Quillnote)
  * https://github.com/clach04/notally_conversion - Conversion tools for [Notally](https://github.com/OmGodse/Notally) notes
