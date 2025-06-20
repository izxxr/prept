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

    This class provides interface for interacting with the file at
    generation time, usually using :ref:`file processors <guide-dynamic-generation--file-processors>`.

    Attributes
    ~~~~~~~~~~
    boilerplate: :class:`BoilerplateInfo`
        The boilerplate that the file is associated to.
    """

    def __init__(
        self,
        boilerplate: BoilerplateInfo,
        filename: str,
        path: pathlib.Path,
        output_path: pathlib.Path,
    ):
        self._path = path
        self._output_path = output_path
        self.boilerplate = boilerplate
        self.filename = filename
        self.process_path_template = True
        self.process_content_template = True

    @property
    def filename(self) -> str:
        """The name of this file.

        This property can be updated at generation time to dynamically
        update the name of file in generated projects.

        Updating this property is a shorthand equivalent of updating
        :attr:`.output_path` file name.
        """
        return self._filename

    @filename.setter
    def filename(self, value: str) -> None:
        if not isinstance(value, str):
            raise ValueError('filename must be a string')

        self._filename = value
        self._output_path = self._output_path.with_name(value)

    @property
    def path(self) -> pathlib.Path:
        """The path of boilerplate file.

        This is the path where the file exists in the boilerplate, not
        the output directory. Use :attr:`.output_path` for path of output
        file.
        """
        return self._path

    @property
    def output_path(self) -> pathlib.Path:
        """The path of output file.

        This is the path where the generated file will be created, not the
        path where file exists in the boilerplate, use :attr:`.path` for
        that.
        """
        return self._output_path

    @property
    def process_path_template(self) -> bool:
        """Flag indicating whether this file's path will be processed by template provider.

        This is True by default and could be set to False to prevent this
        file's path from being processed at generation time.
        """
        return self._process_path_template

    @process_path_template.setter
    def process_path_template(self, value: bool) -> None:
        self._process_path_template = value

    @property
    def process_content_template(self) -> bool:
        """Flag indicating whether this file's content will be processed by template provider.

        This is True by default and could be set to False to prevent this file's
        content from being processed at generation time.
        """
        return self._process_content_template

    @process_content_template.setter
    def process_content_template(self, value: bool) -> None:
        self._process_content_template = value

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
