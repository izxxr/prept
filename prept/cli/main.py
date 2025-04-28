# Copyright (C) Izhar Ahmad 2025-2026

from __future__ import annotations

from prept.commands import commands_list

import click

__all__ = (
    'cli',
)

@click.group()
def cli():
    """CLI tool for managing and generating boilerplates."""

for command in commands_list:
    cli.add_command(command)
