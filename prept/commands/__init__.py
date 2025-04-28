"""
prept.commands
~~~~~~~~~~~~~~

Implementation of Prept commands.
"""

from prept.commands.init import *
from prept.commands.new import *

__all__ = (
    'commands_list',
)

commands_list = (
    init,
    new,
)
