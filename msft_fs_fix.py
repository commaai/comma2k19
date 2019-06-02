#!/usr/bin/python3
"""
This script is a workaround for Microsoft-based filesystems (exFat, NTFS etc):
If you have a non-Microsoft filesystem with sufficient space, copy the 2k19
dataset to that filesystem, say in directory <dir> and use this script as

python3 msft_fs_fix.py <dir>

This will replace all pipes in the comma2k19 dataset with underscores.
"""
import os
import shutil
import sys

NUMBER_OF_CHUNKS = 10


def fix_pipe(base):
    for d in filter(lambda s: '|' in s, os.listdir(base)):
        old = os.path.join(base, d)
        new = os.path.join(base, d.replace('|', '_'))
        try:
            os.makedirs(new, exist_ok=False)
            contents = map(lambda s: os.path.join(old, s), os.listdir(old))
            for f in contents:
                shutil.move(f, os.path.join(new))
            os.rmdir(old)
        except Exception as e:
            print('New directory already exists \
                    -- did you execute this script already?')
            raise e


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage: python msft_fs_fix.py <path to 2k19 dataset>')
        sys.exit(1)
    dataset_dir = sys.argv[1]
    bases = ['Chunk_%d/' % i for i in range(1, NUMBER_OF_CHUNKS + 1)]

    bases = map(lambda c: os.path.join(dataset_dir, c), bases)
    bases = list(filter(os.path.isdir, bases))
    assert len(bases) == NUMBER_OF_CHUNKS, \
        "Could only find {} out of {} chunks in directory {}".format(
        len(bases), NUMBER_OF_CHUNKS, dataset_dir)

    map(fix_pipe, bases)
