# Copyright (C) Izhar Ahmad 2025-2026
# This project is under the MIT license

from __future__ import annotations

from typing import Any
from prept.boilerplate import BoilerplateInfo

import click

__all__ = (
    'BOILERPLATE',
)

class BoilerplateParamType(click.ParamType):
    """CLI parameter type that resolves a value to :class:`BoilerplateInfo`.

    This internally uses the :class:`BoilerplateInfo.resolve` method and follows
    the same resolution order.
    """

    name = "boilerplate"

    def convert(self, value: Any, param: click.Parameter | None, ctx: click.Context | None) -> BoilerplateInfo:
        if isinstance(value, BoilerplateInfo):
            return value

        # resolve() raises InvalidConfig, ConfigNotFound, or BoilerplateNotFound errors
        # which are all inherited from click.ClickException so they are handled properly.
        return BoilerplateInfo.resolve(value)

BOILERPLATE = BoilerplateParamType()
