"""
prept.commands
~~~~~~~~~~~~~~

Implementation of Prept commands.
"""

from prept.commands.init import *
from prept.commands.new import *
from prept.commands.install import *
from prept.commands.list import *
from prept.commands.info import *
from prept.commands.uninstall import *

__all__ = (
    'commands_list',
)

commands_list = (
    init,
    new,
    install,
    list_bps,
    info,
    uninstall,
)
