# Copyright (C) Izhar Ahmad 2025-2026

from __future__ import annotations

from typing import Any
from prept import utils
from prept.cli import outputs
from prept.cli.params import BOILERPLATE_INSTALLABLE
from prept.cli.status import StatusUpdate
from prept.errors import BoilerplateNotFound
from prept.boilerplate import BoilerplateInfo

import os
import stat
import errno
import shutil
import click

__all__ = (
    'install',
)


# This is adapted from https://stackoverflow.com/a/1214935
def _handle_rm_read_only(func: Any, path: str, exc: BaseException):
    if not isinstance(exc, PermissionError):
        raise
    if func in (os.rmdir, os.remove, os.unlink) and exc.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO) # 0777
        func(path)
    else:
        raise


@click.command()
@click.pass_context
@click.argument(
    'boilerplate',
    type=BOILERPLATE_INSTALLABLE,
    required=True,
)
def install(ctx: click.Context, boilerplate: BoilerplateInfo):
    """Installs a boilerplate globally.

    Global installations allow generation from boilerplates directly using
    prept new BOILERPLATE using boilerplate name instead of having to pass
    paths.

    BOILERPLATE can be a path to a valid boilerplate directory (containing
    preptconfig.json) that is to be installed. If current working directory
    is the boilerplate template, use the "prept install ." command.

    It is also possible to install boilerplates through Git by passing a
    repository URL with "git+" suffix. Git must be installed and on PATH
    for this mode of installation.

    Examples:

    * prept install ./basic-boilerplate                     (install from path)
    * prept install git+https://github.com/user/repo.git    (install from git)
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

        if not click.confirm(outputs.cli_msg('Proceed and overwrite current installation?')):
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

        with StatusUpdate(
            message=outputs.cli_msg(f'├── Copying \'{boilerplate.path.name / file}\''),
            error_message=f'Copying of {bp_file} failed with following error:',
        ):
            os.makedirs(target_dir, exist_ok=True)
            shutil.copy(bp_file, target_dir)

    click.echo()

    # \b prevents double spacing if version is not present.
    outputs.echo_success(f'Successfully installed {boilerplate.name} {boilerplate.version or '\b'} boilerplate globally.')
    outputs.echo_info(f'Use \'prept new {boilerplate.name}\' to bootstrap a project from this boilerplate.')

    if boilerplate._from_git:
        outputs.echo_info('Cleaning up cloned git repository')
        try:
            shutil.rmtree(boilerplate.path.absolute(), onexc=_handle_rm_read_only)
        except Exception as e:
            raise outputs.wrap_exception(
                e,
                'The following error occured in clean up of git repository:',
                f'Git repository cloned at {boilerplate.path.absolute()} could not be removed. However, boilerplate was installed successfully.'
            ) from None
        else:
            outputs.echo_success('Successfully removed cloned git repository and installed boilerplate')
