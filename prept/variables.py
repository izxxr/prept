# Copyright (C) Izhar Ahmad 2025-2026

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from typing_extensions import Self
from prept.errors import InvalidConfig

if TYPE_CHECKING:
    from prept.boilerplate import BoilerplateInfo

import re

__all__ = (
    'TemplateVariable',
)

PATTERN_VARIABLE_NAME = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


class TemplateVariable:
    """Wrapper class around template variable structure."""
    def __init__(
        self,
        boilerplate: BoilerplateInfo,
        name: str,
        summary: str | None = None,
        required: bool = True,
        default: Any = None,
    ):
        self.boilerplate = boilerplate
        self.name = name
        self.summary = summary
        self.default = default
        self.required = required

    @classmethod
    def _from_data(cls, boilerplate: BoilerplateInfo, name: str, data: dict[str, Any]) -> Self:
        return cls(
            boilerplate=boilerplate,
            name=name,
            summary=data.get("summary"),
            required=data.get("required", True),
            default=data.get("default"),
        )

    @property
    def name(self) -> str:
        """The name of template variable.

        Variable names must pass the following set of rules:

        - Consists of alphanumeric and underscores characters.
        - Must begin with a letter or underscore.
        - Names are case-sensitive.
        """
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str):
            raise InvalidConfig(f'variables.{value}.name', f'Variable name must be a string; got {name!r} of type {type(name).__qualname__}')
        if not PATTERN_VARIABLE_NAME.match(value):
            raise InvalidConfig(f'variables.{value}.name', f'{value!r} is not a valid variable name.')

        self._name = value

    @property
    def summary(self) -> str | None:
        """A summary or brief describing the variable."""
        return self._summary
    
    @summary.setter
    def summary(self, value: str | None) -> None:
        if value is not None and not isinstance(value, str):
            raise InvalidConfig(f'variables.{value}.summary', f'Variables summary must be a string')

        self._summary = value

    @property
    def required(self) -> bool:
        """Whether the variable is required."""
        return self._required

    @required.setter
    def required(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise InvalidConfig(f'variables.{value}.required', f'required must be a boolean value')
        if self.default is not None:
            self._required = False
        else:
            self._required = value

    @property
    def default(self) -> Any:
        """The default value of this variable if variable is not set or None for no default value."""
        return self._default
    
    @default.setter
    def default(self, value: Any) -> Any:
        self._default = value
        self.required = value is not None
