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
    type=click.Path(file_okay=False, dir_okay=True, readable=True, writable=True, path_type=pathlib.Path),
    help=(
        'The output directory in which the generated files are put into.\n\n'
        'This defaults to ``default_generate_directory`` in preptconfig.json if set otherwise '
        'the name of boilerplate is used as default. If the directory does not exist, it is '
        'created by Prept.'
    )
)
@click.option(
    '--var', '-V',
    nargs=2,
    multiple=True,
    required=False,
    default=None,
    help=(
        'The name/value pair of template variables in "-V <name> <value>" format.\n\n'
        'This takes variables corresponding to ``template_variables`` setting in preptconfig.json. If '
        'some variables are not provided through this option, input for them is prompted when command is ran.\n\n'
        'If ``allow_extra_variables`` setting is set to true in configuration, this option allows passing '
        'variables that are not defined in template variables. If setting is false (default), this causes an error '
        'to be thrown.'
    )
)
def new(
    ctx: click.Context,
    boilerplate: BoilerplateInfo,
    output: pathlib.Path | None = None,
    var: list[tuple[str, str]] | None = None,
):
    """Bootstrap project from a boilerplate.

    ``BOILERPLATE`` is the name or path of boilerplate (containing preptconfig.json) to
    generate the project from.
    """
    outputs.echo_info(f'Generating project from boilerplate: {boilerplate.name}')

    if output is None:
        output = pathlib.Path(boilerplate.default_generate_directory)

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
    else:
        outputs.echo_warning(f'Directory \'{output.absolute()}\' already exists!')
        click.echo(outputs.cli_msg('', 'Previous content that can be overwritten will be lost if you proceed.'))

        if not click.confirm(outputs.cli_msg('', 'Do you wish to overwrite existing directory content?')):
            outputs.echo_info('Exited without making any changes.')
            return

    outputs.echo_info('Processing template variables')
    variables = boilerplate._resolve_variables(var or [])

    outputs.echo_info(f'Creating project files at \'{out_abs}\'')
    click.echo()

    genctx = boilerplate._get_generation_context(
        output=output,
        variables=variables,
    )

    for file in boilerplate._get_generated_files():
        bp_file = boilerplate.path / file
        output_dir = output / os.path.dirname(file)

        click.echo(outputs.cli_msg('', f'├── Creating {output.name / file} ... '), nl=False)

        genctx._set_current_file(file.name, bp_file)
        assert genctx._current_file is not None

        try:
            os.makedirs(output_dir, exist_ok=True)
            shutil.copy(bp_file, output_dir)
        except Exception:
            click.secho('ERROR', fg='red')
            raise PreptError(f'Failed to copy boilerplate file {bp_file} to installation directory at {output / file}')

        click.secho('DONE', fg='green')

        if boilerplate._is_template_file(file) and boilerplate.template_provider is not None:
            click.echo(outputs.cli_msg('', f'├── Applying template on {output.name / file} ... '), nl=False)

            content = boilerplate.template_provider().render(genctx)
            with open(output / file, 'wb' if isinstance(content, bytes) else 'w') as f:
                f.write(content)

            click.secho('DONE', fg='green')

    click.echo()
    outputs.echo_success(f'Successfully generated project from {boilerplate.name!r} boilerplate at \'{output.absolute()}\'')
