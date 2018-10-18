#!/usr/bin/env python
"""patches.py
Create a set of patches from the current or given git repository, in the patches subfolder.
Usage:

    $ python make-patches.py [BASE]  

BASE = the hash of the "base" commit after which to start making patches.
If BASE is omitted, patches are made for every commit in the log history.
Patches are made by comparing each commit after BASE with the one before it.
Patches are named based on the timestamp of the commit, so that the patches will sort in order.
Patches are written to the "patches" subfolder of the current directory.
"""

import logging, os, sys, subprocess
import click

log = logging.getLogger(os.path.basename(__file__))


@click.command()
@click.option('--log-level', default=20)
@click.option('--base', default=None)
@click.option('--src', type=click.Path(exists=True), default=None)
@click.option('--dest', type=click.Path(), default=None)
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
