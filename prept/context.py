# Copyright (C) Izhar Ahmad 2025-2026

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping
from types import MappingProxyType
from prept.file import BoilerplateFile

import pathlib

if TYPE_CHECKING:
    from prept.boilerplate import BoilerplateInfo

__all__ = (
    'GenerationContext',
)


class GenerationContext:
    """The boilerplate generation context.

    This class stores contextual and stateful information regarding generation
    of boilerplate files.

    Attributes
    ~~~~~~~~~~
    output_dir: :class:`pathlib.Path`
        The path to output directory where files are being generated.
    """
    def __init__(
        self,
        boilerplate: BoilerplateInfo,
        output_dir: pathlib.Path,
        variables: dict[str, Any] | None = None,
    ):
        self.output_dir = output_dir
        self._variables = variables or {}
        self._boilerplate = boilerplate
        self._current_file = None

    def _set_current_file(self, filename: str, path: pathlib.Path) -> None:
        self._current_file = BoilerplateFile(boilerplate=self.boilerplate, filename=filename, path=path)

    @property
    def boilerplate(self) -> BoilerplateInfo:
        """The boilerplate that is being generated."""
        return self._boilerplate

    @property
    def variables(self) -> Mapping[str, Any]:
        """Read-only mapping of template variables used for generating template files."""
        return MappingProxyType(self._variables)

    @property
    def current_file(self) -> BoilerplateFile:
        """The file currently in process of being generated.

        This property always returns a valid :class:`BoilerplateFile`
        and in a rare and niche case where no file is being generated
        (i.e. generation has not started yet), RuntimeError is raised.
        """
        if self._current_file is None:
            raise RuntimeError('No file is being generated yet')

        return self._current_file

    def set_variable(self, name: str, value: Any) -> None:
        """Sets a template variable.

        If an existing template variable is set by the same name,
        its value is overwritten.
        """
        self._variables[name] = value

    def delete_variable(self, name: str) -> None:
        """Deletes a template variable.

        If template variable does not exist, a KeyError is raised.
        """
        del self._variables[name]
