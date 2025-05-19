# Copyright (C) Izhar Ahmad 2025-2026

from __future__ import annotations

from prept.cli.params import BOILERPLATE
from prept.boilerplate import BoilerplateInfo

import click

__all__ = (
    'info',
)


@click.command()
@click.pass_context
@click.argument(
    'boilerplate',
    required=True,
    type=BOILERPLATE,
)
def info(
    ctx: click.Context,
    boilerplate: BoilerplateInfo,
):
    """Shows information about a boilerplate.
    
    ``BOILERPLATE`` is either path to a boilerplate directory (containing preptconfig.json)
    or name of an installed boilerplate.
    """
    click.echo(f'\n{boilerplate.name}\n{"-" * len(boilerplate.name)}\n')
    click.echo(f'Summary: {boilerplate.summary or "N/A"}')
    click.echo(f'Version: {boilerplate.version or "N/A"}')
    click.echo(f'Configuration: {(boilerplate.path / "preptconfig.json").absolute()}')
    click.echo(f'Variables:')

    for var in boilerplate.template_variables.values():
        click.echo(f'  - {var.name} {f"(required)" if var.required else "\b"}: {var.summary}')

    click.echo()
