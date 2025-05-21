# Copyright (C) Izhar Ahmad 2025-2026
# This project is under the MIT license

from __future__ import annotations

from typing import Any
from prept.boilerplate import BoilerplateInfo

import click

__all__ = (
    'BOILERPLATE',
    'BOILERPLATE_INSTALLABLE',
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

    def __init__(self, *, installed: bool = True, path: bool = True, git: bool = True) -> None:
        self.installed = installed
        self.path = path
        self.git = git

    def convert(self, value: Any, param: click.Parameter | None, ctx: click.Context | None) -> BoilerplateInfo:
        if isinstance(value, BoilerplateInfo):
            return value

        if isinstance(value, str) and value.startswith('git+') and self.git:
            return BoilerplateInfo._clone_from_git(value.lstrip('git+'))

        if self.path:
            try:
                return BoilerplateInfo.from_path(value)
            except Exception:
                pass

        if self.installed:
            return BoilerplateInfo.from_installation(value)

        # resolve() raises InvalidConfig, ConfigNotFound, or BoilerplateNotFound errors
        # which are all inherited from click.ClickException so they are handled properly.
        return BoilerplateInfo.resolve(value)

BOILERPLATE = BoilerplateParamType()
BOILERPLATE_INSTALLED = BoilerplateParamType(installed=True, path=False)
BOILERPLATE_INSTALLABLE = BoilerplateParamType(installed=False)
