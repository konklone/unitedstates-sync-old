Set of scripts to sync data from the output of various github.com/unitedstates repos to their Downloads tabs.

For now, just does bills from the output of [unitedstates/congress](https://github.com/unitedstates/congress):

    ./sync --session=112

To do multiple sessions at once:

    ./sync --session=107,108,109,110,111,112

There's also a `--cache` flag that won't re-zip the JSON files if the zip already exists for that session.