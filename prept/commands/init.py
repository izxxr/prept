# Copyright (C) Izhar Ahmad 2025-2026

from __future__ import annotations

from prept.cli import outputs
from prept.errors import PreptCLIError
from prept.boilerplate import BoilerplateInfo

import click
import pathlib

__all__ = (
    'init',
)


@click.command()
@click.pass_context
@click.argument('name', required=True)
def init(ctx: click.Context, name: str):
    """Initiailize a boilerplate in the current working directory.

    This command simply creates a preptconfig.json configuration file in
    the working directory.

    ``NAME`` is the boilerplate name and must pass following set of rules:

    - Consists of alphanumeric, hyphens, and underscores characters.
    - Must begin with a letter or underscore.
    - Names are *not* case-sensitive.
    """
    path = pathlib.Path('preptconfig.json')
    if path.exists():
        raise PreptCLIError(f'Existing boilerplate configuration found at {path.absolute()}')

    bp = BoilerplateInfo(name, path)
    bp.save()

    outputs.echo_success(f'Initialized a boilerplate at \'{path}\'')
    outputs.echo_info(f'Edit boilerplate information in the preptconfig.json file')
