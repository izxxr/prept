# Copyright (C) Izhar Ahmad 2025-2026

from __future__ import annotations

from typing import IO, Any
from click import _compat as _click_compat
from prept.cli import outputs

import click

__all__ = (
    'PreptError',
    'ConfigNotFound',
    'InvalidConfig',
    'BoilerplateNotFound',
    'TemplateProviderNotFound',
)


class PreptError(Exception):
    """The base class for all exceptions raised by Prept."""


class PreptCLIError(PreptError, click.ClickException):
    """Exception class to aid errors related to CLI.

    This inherits both :class:`PreptError` and :class:`click.ClickException`.
    """
    def __init__(self, message: str, hint: str | None = None) -> None:
        super().__init__(message)

        self.hint = hint

    def format_message(self) -> str:
        message = outputs.cli_msg('ERROR', self.message, prefix_opts={'fg': 'red'})
        hint = outputs.cli_msg('INFO', self.hint, prefix_opts={'fg': 'blue'}) if self.hint else ''
        return "\n".join((message, hint)).strip()

    def show(self, file: IO[Any] | None = None) -> None:
        # HACK: This is a direct copy from ClickException.copy() because
        # that method does not allow modifying the echoed message and we
        # do not want the 'Error: ' prefix.
        if file is None:
            file = _click_compat.get_text_stderr()

        click.echo(self.format_message(), file=file, color=self.show_color)


class ConfigNotFound(PreptCLIError):
    """Error raised when an operation is performed in directory which is not a boilerplate."""

    def __init__(self) -> None:
        super().__init__(
            'No boilerplate configuration found.',
            'Run prept init in the directory to initialize a boilerplate',
        )


class InvalidConfig(PreptCLIError):
    """Error raised when preptconfig.json contains invalid or unprocessable data.

    Parameters
    ~~~~~~~~~~
    key: :class:`str` | None
        The key causing the error.

        If not present, the error is caused by malformed or unparseable
        boilerplate configuration.
    """

    def __init__(
        self,
        key: str | None,
        *args: Any,
        **kwargs: Any,
    ):
        self.key = key
        super().__init__(*args, **kwargs)


class BoilerplateNotFound(PreptCLIError):
    """Error raised when an operation is performed on a boilerplate that is not installed.
    
    Parameters
    ~~~~~~~~~~
    name: :class:`str`
        The name of boilerplate that caused the error.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f'No boilerplate with name {name!r} is installed')


class TemplateProviderNotFound(PreptCLIError):
    """Error raised when template provider is not found, not installed, or has invalid name."""

    def __init__(self, name: str, reason: str) -> None:
        super().__init__(f'The template provider {name!r} is not found or invalid ({reason})')
