# Copyright (C) Izhar Ahmad 2025-2026

from __future__ import annotations

from prept import utils
from prept.cli import outputs
from prept.cli.params import BOILERPLATE_PATH
from prept.errors import BoilerplateNotFound, PreptCLIError
from prept.boilerplate import BoilerplateInfo

import os
import shutil
import click

__all__ = (
    'install',
)

@click.command()
@click.pass_context
@click.argument(
    'boilerplate',
    type=BOILERPLATE_PATH,
    required=True,
)
def install(ctx: click.Context, boilerplate: BoilerplateInfo):
    """Installs a boilerplate globally.

    ``BOILERPLATE`` is the path to a valid boilerplate directory (containing
    preptconfig.json) that is to be installed. If current working directory
    is the boilerplate template, use prept install . (dot in place of BOILERPLATE)

    Global installations allow generation from boilerplates directly using
    prept new BOILERPLATE using boilerplate name instead of having to pass paths.

    This command also exists for future proofing as it will be possible
    to install boilerplates from Git repositories and other third party
    sources as well.
    """
    overwrite = False

    try:
        bp_installed = BoilerplateInfo.from_installation(boilerplate.name)
    except BoilerplateNotFound:
        pass
    else:
        outputs.echo_warning(f'Another boilerplate with name {boilerplate.name!r} is already installed.')
        outputs.echo_info(f'Installed Version: {bp_installed.version or 'N/A'}')
        outputs.echo_info(f'Installing Version: {bp_installed.version or 'N/A'}')

        if not click.confirm(outputs.cli_msg('', 'Proceed and overwrite current installation?')):
            outputs.echo_info('Installation aborted with no changes.')
            return

        overwrite = True

    target = utils.get_prept_dir('boilerplates', boilerplate.name.lower())

    # \b in messages below prevents double spacing if version is not present
    if overwrite:
        outputs.echo_info(f'Installing {boilerplate.name} {boilerplate.version or '\b'} globally (overwrite existing installation)...')
    else:
        outputs.echo_info(f'Installing {boilerplate.name} {boilerplate.version or '\b'} globally...')

    outputs.echo_info(f'From boilerplate at \'{boilerplate.path.absolute()}\' to \'{target.absolute()}\'')
    outputs.echo_info(f'Copying files to installation root at \'{target}\'')
    click.echo()

    for file in boilerplate._get_installation_files():
        bp_file = boilerplate.path / file
        target_dir = target / os.path.dirname(file)

        click.echo(outputs.cli_msg('', f'├── Copying \'{boilerplate.path.name / file}\' ... '), nl=False)

        try:
            os.makedirs(target_dir, exist_ok=True)
            shutil.copy(bp_file, target_dir)
        except Exception:
            click.secho('ERROR', fg='red')
            raise PreptCLIError(f'Failed to copy boilerplate file {bp_file} to installation directory at {target / file}')
        else:
            click.secho('DONE', fg='green')

    click.echo()

    # \b prevents double spacing if version is not present.
    outputs.echo_success(f'Successfully installed {boilerplate.name} {boilerplate.version or '\b'} boilerplate globally.')
    outputs.echo_info(f'Use \'prept new {boilerplate.name}\' to bootstrap a project from this boilerplate.')
