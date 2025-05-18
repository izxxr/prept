# Copyright (C) Izhar Ahmad 2025-2026

from __future__ import annotations

from prept.cli import outputs
from prept.cli.params import BOILERPLATE_INSTALLED
from prept.errors import PreptCLIError
from prept.boilerplate import BoilerplateInfo

import shutil
import click

__all__ = (
    'uninstall',
)

@click.command()
@click.pass_context
@click.argument(
    'boilerplate',
    type=BOILERPLATE_INSTALLED,
    required=True,
)
def uninstall(ctx: click.Context, boilerplate: BoilerplateInfo):
    """Uninstalls a boilerplate.

    ``BOILERPLATE`` is the name of a globally installed boilerplate.
    """
    if not boilerplate.path.exists():
        raise PreptCLIError('This boilerplate is not installed.')
    
    outputs.echo_warning(f'Boilerplate {boilerplate.name} {boilerplate.version or '\b'} will be uninstalled.')

    if not click.confirm(outputs.cli_msg('Do you wish to proceed?')):
        outputs.echo_info('Aborted. No changes were made.')
        return

    outputs.echo_info(f'Removing installation directory from {boilerplate.path.absolute()}')
    try:
        shutil.rmtree(boilerplate.path)
    except Exception as e:
        outputs.echo_error('Failed to uninstall the boilerplate. Installation directory could not be removed.')
        click.echo(outputs.cli_msg('The following error occured:'))
        click.echo(outputs.cli_msg(str(e)))
    else:
        outputs.echo_success(f'Successfully uninstalled {boilerplate.name} {boilerplate.version or '\b'} boilerplate.')
