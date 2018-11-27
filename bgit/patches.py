#!/usr/bin/env python
"""patches.py
Create a set of patches from the current or given git repository, in the patches subfolder.
Usage:

    $ python patches.py [--base BASE --src SRC --dest DEST]

or:

    $ python -m bgit.patches [--base BASE --src SRC --dest DEST]

BASE = the hash of the "base" commit after which to start making patches.
If BASE is omitted, patches are made for every commit in the log history.
Patches are made from the SRC folder (default = the current working directory).
Patches are made by comparing each commit after BASE with the one before it.
Patches are written to the DEST folder (default = the "patches" subfolder of the current directory).
Patches are named by the timestamp + hash of the commit, so the patches will sort chronologically.
Existing patches are not overwritten (but if they were, they wouldn't be different).
"""

import logging, os, sys, subprocess
import click

log = logging.getLogger(os.path.basename(__file__))


@click.command()
@click.option('--log_level', '-l', default=20, help="log level")
@click.option('--base', '-b', default=None, help="the hash of the base revision")
@click.option('--src', '-s', type=click.Path(exists=True), help="source folder, default CWD")
@click.option('--dest', '-d', type=click.Path(), help="destination folder, default CWD/patches")
def main(log_level, base, src, dest):

    logging.basicConfig(level=log_level)

    if src is None:
        src = os.getcwd()
    os.chdir(src)

    if dest is None:
        dest = src + '/patches'
    if not os.path.exists(dest):
        os.makedirs(dest)

    commits = [
        c.strip('\n"').split(' ')
        for c in list(
            reversed(
                subprocess.check_output(['git', 'log', '--format="%H %cI"'])
                .decode('utf-8')
                .split('\n')
            )
        )
    ]

    if base is not None and base in [c[0] for c in commits]:
        commits = commits[[c[0] for c in commits].index(base) :]

    for i in range(1, len(commits)):
        sha1 = commits[i - 1][0]
        sha2, ts = commits[i]
        fb = "%s.%s.patch" % (ts.replace('-', '').replace(':', '').replace('T', ''), sha2)
        patch_fn = os.path.join(dest, fb)
        if not os.path.exists(patch_fn) and sha1 != '' and sha2 != '':
            patch = subprocess.check_output(['git', 'log', '-p', "%s..%s" % (sha1, sha2)])
            with open(patch_fn, 'wb') as f:
                f.write(patch)
            log.info('wrote patch: %s' % os.path.relpath(patch_fn, dest))


if __name__ == '__main__':
    main()
