# Copyright (C) Izhar Ahmad 2025-2026

from __future__ import annotations

from typing import Any, Iterator
from typing_extensions import Self
from packaging.version import Version, InvalidVersion
from prept.errors import InvalidConfig, ConfigNotFound, BoilerplateNotFound
from prept import utils

import re
import os
import json
import pathspec
import pathlib

__all__ = (
    'BoilerplateInfo',
)


PATTERN_BOILERPLATE_NAME = re.compile(r'^[A-Za-z_][A-Za-z0-9_-]*$')
DEFAULT_IGNORED_PATHS = {'preptconfig.json'}


class BoilerplateInfo:
    """Represents a boilerplate.

    This is a wrapper class for information stored in preptconfig.json.
    """
    def __init__(
        self,
        name: str,
        path: pathlib.Path,
        summary: str | None = None,
        version: Version | str | None = None,
        ignore_paths: list[str] | None = None,
        default_generate_directory: str | None = None,
    ):
        self._path = path
        self.ignore_paths = ignore_paths or []
        self.name = name
        self.summary = summary
        self.version = version
        self.default_generate_directory = default_generate_directory

    def _get_generated_files(self) -> Iterator[pathlib.Path]:
        ignore_paths = set(self._ignore_paths).union(DEFAULT_IGNORED_PATHS)
        spec = pathspec.PathSpec.from_lines("gitwildmatch", ignore_paths)

        for file in spec.match_tree(self.path, negate=True):
            yield pathlib.Path(self.path / file).relative_to(self.path)

    def _get_installation_files(self) -> Iterator[pathlib.Path]:
        spec = pathspec.PathSpec.from_lines("gitwildmatch", [])

        for file in spec.match_tree(self.path, negate=True):
            yield pathlib.Path(self.path / file).relative_to(self.path)

    @property
    def path(self) -> pathlib.Path:
        """The path pointing towards this boilerplate."""
        return self._path

    @property
    def name(self) -> str:
        """The name of boilerplate.

        Boilerplate names must pass the following set of rules:

        - Consists of alphanumeric, hyphens, and underscores characters.
        - Must begin with a letter or underscore.
        - Names are *not* case-sensitive.
        """
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str):
            raise InvalidConfig('name', f'Boilerplate name must be a string; got {name!r} of type {type(name).__qualname__}')
        if not PATTERN_BOILERPLATE_NAME.match(value):
            raise InvalidConfig('name', f'{value!r} is not a valid boilerplate name.')

        self._name = value

    @property
    def summary(self) -> str | None:
        """A summary or brief describing the boilerplate."""
        return self._summary
    
    @summary.setter
    def summary(self, value: str | None) -> None:
        if value is not None and not isinstance(value, str):
            raise InvalidConfig('summary', f'Boilerplate summary must be a string')

        self._summary = value

    @property
    def version(self) -> Version | None:
        """The version of boilerplate.

        If provided, version must follow the specification described
        in PEP 440: https://peps.python.org/pep-0440/
        """
        return self._version
 
    @version.setter
    def version(self, value: Version | str | None) -> None:        
        if value is not None and not isinstance(value, (Version, str)):
            raise InvalidConfig('version', f'{version!r} cannot be parsed as a boilerplate version')

        try:
            self._version = Version(value) if isinstance(value, str) else value
        except InvalidVersion:
            raise InvalidConfig(
                'version',
                f'{value!r} is not a valid boilerplate version',
                'Versions must follow the specification described by PEP 440: https://peps.python.org/pep-0440/'
            )
        
    @property
    def ignore_paths(self) -> list[str]:
        """List of paths that are not included in code generated from boilerplate.

        This option is useful in ignoring any irrelevant paths such as ``.git``. Note
        that Prept automatically ignores boilerplate configuration file regardless of
        the value of this attribute.
        """
        return self._ignore_paths

    @ignore_paths.setter
    def ignore_paths(self, value: list[str] | None) -> None:
        if value is None:
            value = []
        if list(filter(lambda v: not isinstance(v, str), value)):
            raise InvalidConfig('ignore_paths', 'ignore_paths cannot contain non-string entries')

        self._ignore_paths = value

    @property
    def default_generate_directory(self) -> str:
        """The default directory that boilerplate generates code in.

        This directory is used (or created) if user does not specify
        `-O` in "prept new" command.

        If not provided, defaults to the name of boilerplate.
        """
        return self._default_generate_directory or self._name

    @default_generate_directory.setter
    def default_generate_directory(self, value: str | None) -> None:
        if value is not None and not isinstance(value, str):
            raise InvalidConfig('default_generate_directory', 'default_generate_directory must be a string')

        self._default_generate_directory = value

    @classmethod
    def from_path(cls, path: pathlib.Path | str) -> Self:
        """Loads boilerplate information from its path.

        Raises :class:`ConfigNotFound` or :class:`InvalidConfig` if boilerplate
        configuration does not exist or is invalid.

        Parameters
        ~~~~~~~~~~
        path: :class:`pathlib.Path` | :class:`str`
            The path to boilerplate directory.
        """
        if not isinstance(path, pathlib.Path):
            path = pathlib.Path(path)

        try:
            with open(path / 'preptconfig.json', 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            if isinstance(e, FileNotFoundError):
                raise ConfigNotFound
            else:
                raise InvalidConfig(None)

        if 'name' not in data:
            raise InvalidConfig(key='name', missing=True)

        return cls(
            name=data['name'],
            path=path,
            summary=data.get('summary'),
            version=data.get('version'),
            ignore_paths=data.get('ignore_paths'),
            default_generate_directory=data.get('default_generate_directory'),
        )
    
    @classmethod
    def from_installation(cls, name: str) -> Self:
        """Loads boilerplate from the installation.

        Raises :class:`ConfigNotFound` or :class:`InvalidConfig` if boilerplate
        configuration does not exist or is invalid, respectively. If boilerplate
        does not exist, then :class:`BoilerplateNotFound` is raised.

        Parameters
        ~~~~~~~~~~
        name: :class:`str`
            The name of boilerplate.
        """
        bp_dir = utils.get_prept_dir('boilerplates', name)

        if not bp_dir.exists():
            raise BoilerplateNotFound(name)
        
        return cls.from_path(bp_dir)

    @classmethod
    def resolve(cls, value: Any) -> Self:
        """Resolves a boilerplate from given value.

        If boilerplate cannot be resolved, :class:`BoilerplateNotFound` error
        is raised.
        """
        if isinstance(value, (pathlib.Path, str)) and os.path.exists(value):
            try:
                return cls.from_path(value)
            except Exception:
                # If from_path() fails (e.g. no preptconfig.json in given path), we
                # silently ignore it and continue to next way of resolution.
                pass

        return cls.from_installation(str(value))

    def dump(self) -> dict[str, Any]:
        """Returns the boilerplate in raw data form.

        The result is compatible with the preptconfig.json schema.
        """
        data: dict[str, Any] = {
            "name": self._name,
        }

        if self._summary:
            data['summary'] = self._summary

        if self._version:
            data['version'] = self._version
        
        if self._ignore_paths:
            data['ignore_paths'] = self._ignore_paths

        if self._default_generate_directory:
            data['default_generate_directory'] = self._default_generate_directory

        return data

    def save(self) -> None:
        """Saves the boilerplate configuration.

        If configuration is not already present (boilerplate is not initialized), it
        is saved hence initializing the boilerplate.
        """        
        with open(self.path, 'w') as f:
            json.dump(self.dump(), f, indent=4)
