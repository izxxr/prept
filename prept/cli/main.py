# Copyright (C) Izhar Ahmad 2025-2026

from __future__ import annotations

from prept.commands import commands_list

import click
import sys

__all__ = (
    'cli',
)

@click.group()
def cli():
    """CLI tool for managing and generating boilerplates."""
    # This facilitates using user defined components such as template
    # providers that are defined in module present in CWD
    sys.path.insert(0, '.')

for command in commands_list:
    cli.add_command(command)
