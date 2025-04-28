# Copyright (C) Izhar Ahmad 2025-2026

from __future__ import annotations

import click
import pathlib

__all__ = (
    'get_prept_dir',
)

def get_prept_dir(*subdirs: str) -> pathlib.Path:
    """Gets the directory for Prept.
    
    subdirs can be passed to get path to a subdirectory such as
    .prept/boilerplates/.
    """
    path = pathlib.Path(click.get_app_dir('prept'))
    return path / pathlib.Path(*subdirs)
