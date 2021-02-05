'''
This script is a workaround for Microsoft-based filesystems (exFat, NTFS etc).
These filesystems don't allow the vertical pipe ('|') in paths.
So, instead of unzipping files manually, run this script which will replace
all pipes in path names in the zip files by underscores.

Usage:
python3 unzip_msft_fs.py <dataset dir> <goal dir>
'''

import multiprocessing
import os
import shutil
import sys
import zipfile

NUMBER_OF_CHUNKS = 10


def unzip_replace(zip_dir, zip_name, extract_dir,
                  filter_predicate, replace_me, replace_by):
    zip_path = os.path.join(zip_dir, zip_name)
    z = zipfile.ZipFile(zip_path)
    for f in z.infolist():
        if filter_predicate(f):
            old = f.filename
            f.filename = f.filename.replace(replace_me, replace_by)
            z.extract(f, extract_dir)


def fix_pipe(base):
    """
    Given unzipped directory "base",
    creates new directories with | replaced with _,
    moves all contents into their respective new directories
    and then deletes the old (now empty) directories that contain |.
    """
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


def map_fn(args):
    unzip_replace(args['dir'], args['.zip'], args['extract'],
                  lambda f: '|' in f.filename, '|', '_')
    print('Finished unzipping {}'.format(
        os.path.join(args['dir'], args['.zip'])))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('python3 unzip_msft_fs.py <dataset dir> <goal dir>')
        sys.exit(1)

    dataset_dir = sys.argv[1]
    goal_dir = sys.argv[2]

    if not os.path.isdir(goal_dir):
        print('Creating directories for you...')
        os.makedirs(goal_dir)

    bases = ['Chunk_%d.zip' % i for i in range(1, NUMBER_OF_CHUNKS + 1)]
    """
    Assuming that your hard drive is slow,
    so it is ok too have more processes than cores
    i.e. overhead of managing more processes << time spent unzipping
    """
    p = multiprocessing.Pool(len(bases))

    # bbases: bases wih base :)
    bbases = map(lambda c: os.path.join(dataset_dir, c), bases)
    bbases = list(filter(os.path.isfile, bbases))
    assert len(bbases) == NUMBER_OF_CHUNKS, \
        "Could only find {} out of {} chunks in directory {}".format(
        len(bbases), NUMBER_OF_CHUNKS, dataset_dir)

    for i, b in enumerate(bases):
        bases[i] = {
            'dir': dataset_dir,
            'extract': goal_dir,
            '.zip': b
        }
    p.map(map_fn, bases)

    bbases = list(map(lambda b: b.replace('.zip', ''), bbases))
    bbases = list(filter(os.path.isdir, bbases))
    assert len(bbases) == NUMBER_OF_CHUNKS, \
        "Could only find {} out of {} chunks in directory {}".format(
        len(bbases), NUMBER_OF_CHUNKS, dataset_dir)
