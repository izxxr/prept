# Copyright (C) Izhar Ahmad 2025-2026

from __future__ import annotations

from typing import IO, Any
from click import _compat as _click_compat
from prept.cli import outputs

import click

__all__ = (
    'PreptError',
    'PreptCLIError',
    'ConfigNotFound',
    'InvalidConfig',
    'BoilerplateNotFound',
    'TemplateProviderNotFound',
    'EngineNotFound',
)


class PreptError(Exception):
    """The base class for all exceptions raised by Prept."""


class PreptCLIError(PreptError, click.ClickException):
    """Exception class to aid errors related to CLI.

    This inherits both :class:`PreptError` and :class:`click.ClickException`.

    .. versionchanged:: 0.2.0

        Multi-line message and hint now support proper indentation formatting
        in error output.
    """
    def __init__(self, message: str, hint: str | None = None) -> None:
        super().__init__(message)

        self.hint = hint

    def format_message(self) -> str:
        message_lines = self.message.splitlines()
        if not message_lines:
            return ''

        message = outputs.cli_msg('ERROR', message_lines.pop(0), prefix_opts={'fg': 'red'})
        for line in message_lines:
            message += '\n' + outputs.cli_msg(line)

        hint_lines = self.hint.splitlines() if self.hint else []
        if not hint_lines:
            return message

        hint = outputs.cli_msg('INFO', hint_lines.pop(0), prefix_opts={'fg': 'blue'})
        for line in hint_lines:
            hint += '\n' + outputs.cli_msg(line)

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

    def __init__(self, spec: str, reason: str) -> None:
        super().__init__(f'Failed to resolve template provider from spec {spec!r} ({reason})')


class EngineNotFound(PreptCLIError):
    """Error raised when generation engine could not be found."""

    def __init__(self, spec: str, reason: str) -> None:
        super().__init__(f'Failed to resolve generation engine from spec {spec!r} ({reason})')
