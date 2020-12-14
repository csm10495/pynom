'''
script to create docs
'''

import os
import re
import shutil
import subprocess
import sys

if __name__ == '__main__':
    assert subprocess.call([
        sys.executable,
        '-m',
        'pip',
        'install',
        'setuptools',
        'pdoc3',
    ]) == 0, 'Unable to install pdoc3'

    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    assert subprocess.call([
        sys.executable,
        '-m',
        'pdoc',
        '--html',
        'pynom',
        '-o',
        'docs_tmp',
        '-f'
    ]) == 0, 'Unable to generate docs via pdoc'

    # remove existing docs dir
    shutil.rmtree('docs', ignore_errors=True)

    # remove extra dir nesting and move back to docs/
    shutil.move('docs_tmp/pynom', 'docs')
    os.rmdir('docs_tmp')