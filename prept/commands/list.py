# Copyright (C) Izhar Ahmad 2025-2026

from __future__ import annotations

from prept import utils
from prept.cli import outputs
from prept.boilerplate import BoilerplateInfo

import os
import click

__all__ = (
    'list_bps',
)

@click.command(name='list')
@click.pass_context
def list_bps(ctx: click.Context):
    """List installed boilerplates."""
    bps_dir = utils.get_prept_dir('boilerplates')
    total = 0
    listed = 0

    click.echo('Listing installed boilerplates...\n')

    for bp in os.listdir(bps_dir):
        if not (bps_dir / bp / 'preptconfig.json').exists():
            continue

        total += 1
        try:
            bp = BoilerplateInfo.from_installation(bp)
        except Exception:
            continue
        else:
            click.echo(f'- {bp.name} {bp.version or ""}')
            listed += 1

    if total == 0:
        outputs.echo_info('No boilerplates are installed.')
    else:
        click.echo(f'\nListed {listed} of {total} installed boilerplates.')

        if total != listed:
            outputs.echo_warning(f'{total - listed} boilerplates were installed but could not be loaded.')
