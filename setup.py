from setuptools import setup

setup(
    name='jrti_game',
    version='0.1',
    description='Just Read the Instructions, the game',
    author='Petr Viktorin',
    author_email='encukou@gmail.com',
    license='MIT',
    url='https://pyweek.org/e/instructions/',
    packages=['jrti_game'],
    install_requires=['pyglet == 1.2.4'],
)
