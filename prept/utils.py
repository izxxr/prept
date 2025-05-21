# Copyright (C) Izhar Ahmad 2025-2026

from __future__ import annotations

import click
import pathlib
import os

__all__ = (
    'UNDEFINED',
    'get_prept_dir',
)


class _Undefined:
    ...

UNDEFINED = _Undefined()


def get_prept_dir(*subdirs: str, mk: bool = False) -> pathlib.Path:
    """Gets the directory for Prept.
    
    subdirs can be passed to get path to a subdirectory such as
    .prept/boilerplates/.
    """
    path = pathlib.Path(click.get_app_dir('prept'))
    path = path / pathlib.Path(*subdirs)

    if not path.exists() and mk:
        os.makedirs(path)

    return path
