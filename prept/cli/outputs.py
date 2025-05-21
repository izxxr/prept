# Copyright (C) Izhar Ahmad 2025-2026

from __future__ import annotations

from prept.errors import PreptCLIError
from typing import Any

import traceback
import click

__all__ = (
    'cli_msg',
    'echo_error',
    'echo_success',
    'echo_info',
    'echo_warning',
)


def cli_msg(
    prefix: str,
    message: str | None = None,
    padding: int = 8,
    prefix_opts: dict[str, Any] | None = None,
    message_opts: dict[str, Any] | None = None,
):
    if message is None:
        message = prefix
        prefix = ''

    pref = click.style(f'{prefix:<{padding}}', **(prefix_opts or {}))
    msg = click.style(message, **(message_opts or {}))
    return pref + msg

def echo_error(message: str):
    click.echo(cli_msg('ERROR', message, prefix_opts={'fg': 'red'}))

def echo_success(message: str):
    click.echo(cli_msg('SUCCESS', message, prefix_opts={'fg': 'green'}))

def echo_info(message: str):
    click.echo(cli_msg('INFO', message, prefix_opts={'fg': 'blue'}))

def echo_warning(message: str):
    click.echo(cli_msg('WARNING', message, prefix_opts={'fg': 'yellow'}))

def wrap_exception(
    exc: Exception,
    message: str = 'The following error occurred and could not be handled:',
    hint: str | None = None,
) -> PreptCLIError:
    message = message + '\n' + ''.join(traceback.format_tb(exc.__traceback__))
    return PreptCLIError(message, hint)
