# Copyright (C) Izhar Ahmad 2025-2026
# This project is under the MIT license

from __future__ import annotations

from typing import TYPE_CHECKING
from prept.errors import PreptError
from prept.cli import outputs
from prept.cli.params import BOILERPLATE

import click
import shutil
import os
import pathlib

if TYPE_CHECKING:
    from prept.boilerplate import BoilerplateInfo

__all__ = (
    'new',
)

@click.command()
@click.pass_context
@click.argument(
    'boilerplate',
    required=True,
    type=BOILERPLATE,
)
@click.option(
    '--output', '-O',
    required=False,
    default=None,
    prompt=(
        outputs.cli_msg('OUTPUT', 'Where should the project be generated?\n', prefix_opts={'fg': 'black'}) +
        outputs.cli_msg('', 'If not provided, a new directory with the name of boilerplate is created.\n\n') + 
        outputs.cli_msg('', 'Output')
    ),
    type=click.Path(file_okay=False, dir_okay=True, readable=True, writable=True, path_type=pathlib.Path),
    help='The output directory in which the generated files are put into.',
)
def new(
    ctx: click.Context,
    boilerplate: BoilerplateInfo,
    output: pathlib.Path,
):
    """Generate a skeleton project from a boilerplate.

    BOILERPLATE is the name or path of boilerplate to generate from.
    """
    outputs.echo_info(f'Generating project from boilerplate: {boilerplate.name}')

    out_abs = output.absolute()  # for outputs
    if not output.exists():
        outputs.echo_info(f'No existing directory found. Creating project directory at \'{out_abs}\'')
        try:
            output.mkdir()
        except Exception as e:
            outputs.echo_error(f'({e.__class__.__name__}) {e}')
            outputs.echo_error(f'Failed to create project directory, aborting.')
            return
        else:
            outputs.echo_info(f'Successfully created project directory at {out_abs}')

    outputs.echo_info(f'Creating project files at \'{out_abs}\'')
    click.echo()

    for file in boilerplate._get_generated_files():
        bp_file = boilerplate.path / file
        output_dir = output / os.path.dirname(file)

        click.echo(outputs.cli_msg('', f'├── Creating {output.name / file} ... '), nl=False)

        try:
            os.makedirs(output_dir, exist_ok=True)
            shutil.copy(bp_file, output_dir)
        except Exception:
            click.secho('ERROR', fg='red')
            raise PreptError(f'Failed to copy boilerplate file {bp_file} to installation directory at {output / file}')
        else:
            click.secho('DONE', fg='green')

    click.echo()
    outputs.echo_success(f'Successfully generated project from {boilerplate.name!r} boilerplate at \'{output.absolute()}\'')
