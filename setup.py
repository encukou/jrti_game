from setuptools import setup

setup(
    name='jrti_game',
    version='1.0.3',
    description='Just Read the Instructions, the game',
    author='Petr Viktorin',
    author_email='encukou@gmail.com',
    license='MIT',
    url='https://pyweek.org/e/instructions/',
    packages=['jrti_game'],
    install_requires=[
        'pyglet == 1.2.4',
        'pypng == 0.0.18',
        'attrs == 17.2.0',
    ],
    entry_points={
        'console_scripts': [
            'jrti-game = jrti_game:main',
        ],
    },
    package_data={'jrti_game': ['data/*', 'data/*/*']},
)
