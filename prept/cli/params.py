# Copyright (C) Izhar Ahmad 2025-2026
# This project is under the MIT license

from __future__ import annotations

from typing import Any
from prept.boilerplate import BoilerplateInfo

import click

__all__ = (
    'BOILERPLATE',
    'BOILERPLATE_PATH',
    'BOILERPLATE_INSTALLED',
)

class BoilerplateParamType(click.ParamType):
    """CLI parameter type that resolves a value to :class:`BoilerplateInfo`.

    This internally uses the :class:`BoilerplateInfo.resolve` method and follows
    the same resolution order.

    Parameters
    ~~~~~~~~~~
    exclude_installed: :class:`bool`
        Controls whether resolution includes lookup through installed boilerplates.

        If true, only path resolution is done. Defaults to False.
    """
    name = "boilerplate"

    def __init__(self, *, exclude_installed: bool = False, exclude_path: bool = False) -> None:
        if exclude_path and exclude_installed:
            raise TypeError('exclude_path and exclude_installed are mututally exclusive')

        self.exclude_installed = exclude_installed
        self.exclude_path = exclude_path

    def convert(self, value: Any, param: click.Parameter | None, ctx: click.Context | None) -> BoilerplateInfo:
        if isinstance(value, BoilerplateInfo):
            return value

        if self.exclude_installed:
            return BoilerplateInfo.from_path(value)

        if self.exclude_path:
            return BoilerplateInfo.from_installation(value)

        # resolve() raises InvalidConfig, ConfigNotFound, or BoilerplateNotFound errors
        # which are all inherited from click.ClickException so they are handled properly.
        return BoilerplateInfo.resolve(value)

BOILERPLATE = BoilerplateParamType()
BOILERPLATE_PATH = BoilerplateParamType(exclude_installed=True)
BOILERPLATE_INSTALLED = BoilerplateParamType(exclude_path=True)
