"""
Prept
~~~~~

CLI tool for managing and generating boilerplates.
"""

__version__ = '0.1.0'
__author__  = 'Izhar Ahmad <izxxr>'

from prept.cli.main import cli as __cli__
from prept.boilerplate import *
from prept.variables import *
from prept.providers import *
from prept.context import *
from prept.errors import *
from prept.file import *
from prept.engine import *
