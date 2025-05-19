# Copyright (C) Izhar Ahmad 2025-2026

from __future__ import annotations

from typing import Any
from typing_extensions import Self
from prept.cli import outputs
from prept.errors import PreptCLIError

import click
import types

__all__ = (
    'StatusUpdate',
)


class StatusUpdate:
    def __init__(
        self,
        message: str,
        error_message: str = 'The following error occured and could not be handled:',
        hint: str | None = None,
        reraise_prept_error: bool = True,
        **echo_kwargs: Any
    ) -> None:
        self._message = message
        self._echo_kwargs = echo_kwargs
        self._error_message = error_message
        self._hint = hint
        self._reraise_prept_error = reraise_prept_error

    def __enter__(self) -> Self:
        click.secho(self._message + ' ... ', nl=False, **self._echo_kwargs)
        return self

    def __exit__(self, exc_type: type[Exception] | None, exc: Exception | None, tb: types.TracebackType | None) -> None:
        if exc is None:
            click.secho('DONE', fg='green')
            return

        click.secho('ERROR', fg='red')
        click.echo()

        if isinstance(exc, PreptCLIError) and self._reraise_prept_error:
            raise exc from None

        raise outputs.wrap_exception(exc, self._error_message, self._hint) from None
