from setuptools import setup

import prept

with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()

setup(
    name='prept',
    version=prept.__version__,
    py_modules=['prept'],
    install_requires=requirements,
    entry_points={
        'console_scripts': ['prept = prept.cli.main:cli'],
    },
)
