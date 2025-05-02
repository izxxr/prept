# Copyright (C) Izhar Ahmad 2025-2026

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, overload

import pathlib

if TYPE_CHECKING:
    from prept.boilerplate import BoilerplateInfo

__all__ = (
    'BoilerplateFile',
)


class BoilerplateFile:
    """Represents a file from a boilerplate.

    Attributes
    ~~~~~~~~~~
    boilerplate: :class:`BoilerplateInfo`
        The boilerplate that the file is associated to.
    filename: :class:`str`
        The name of file.
    path: :class:`pathlib.Path`
        The path towards file. This is the path in the boilerplate
        directory, not the directory in which file is being generated.
    """

    def __init__(
        self,
        boilerplate: BoilerplateInfo,
        filename: str,
        path: pathlib.Path,
    ):
        self.boilerplate = boilerplate
        self.filename = filename
        self.path = path

    @overload
    def read(self) -> str:
        ...

    @overload
    def read(self, *, binary: Literal[False]) -> str:
        ...

    @overload
    def read(self, *, binary: Literal[True]) -> bytes:
        ...

    def read(self, *, binary: bool = False) -> str | bytes:
        """Opens the file, reads its content, and closes it.

        Attributes
        ~~~~~~~~~~
        binary: :class:`bool`
            Whether to open file in binary mode.
        """
        return self.path.read_bytes() if binary else self.path.read_text()
