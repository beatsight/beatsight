#!/usr/bin/env python3
# encoding:utf-8

import os
import subprocess
import argparse
import sys

def remove_unused(source_dir):
    ...

ignore_list = ['manage.py']

def compile_py3(source_dir):
    g = os.walk(source_dir)
    subprocess.check_output(f'{sys.executable} -m compileall -b {source_dir}', shell=True)
    for path, d, filelist in g:
        for filename in filelist:
            if filename in ignore_list:
                continue

            if os.path.splitext(filename)[-1] == '.py':
                os.remove(os.path.join(path, filename))
                print('compile {}'.format(os.path.join(path, filename)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scramble python opcodes table')
    parser.add_argument('--python-source', dest='src', type=str,
                        help='Python source code', required=True)
    args = parser.parse_args()
    source_directory = os.path.abspath(args.src)

    compile_py3(source_directory)
