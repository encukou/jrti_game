import sys
import zipapp
import zipfile
import pathlib
import tempfile
import textwrap
import subprocess

pyz_name = 'jrti_game.pyz'

with tempfile.TemporaryDirectory() as tmp:
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--target', tmp,
                    'pyglet == 1.2.4',
                    'pypng == 0.0.18',
                    'attrs == 17.2.0',
                   ],
                   check=True)

    for line in subprocess.run(['git', 'ls-tree', '--name-only', '-r', 'HEAD'],
                   stdout=subprocess.PIPE,
                   encoding='utf-8',
                   check=True).stdout.splitlines():
        path = pathlib.Path(line)
        (tmp / path).parent.mkdir(parents=True, exist_ok=True)
        with path.open('rb') as src, (tmp / path).open('wb') as dest:
            dest.write(src.read())

    zipapp.create_archive(
        tmp,
        pyz_name,
        interpreter='/usr/bin/env python3',
        main='jrti_game:main',
    )
