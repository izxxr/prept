# Copyright (C) Izhar Ahmad 2025-2026

from __future__ import annotations

from typing import Any
from prept.errors import SpecResolutionError

import click
import pathlib
import importlib
import os

__all__ = (
    'UNDEFINED',
    'get_prept_dir',
    'resolve_from_module_spec_format',
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


def resolve_from_module_spec_format(spec: str, key: str | None = None) -> Any:
    parts = spec.strip().split(':')
    if not parts:
        raise SpecResolutionError(key, 'This key cannot be empty')
    if len(parts) != 2:
        raise SpecResolutionError(key, 'Invalid value, must be in format "module:attr"')
    
    module_name, attr_name = parts
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:
        raise SpecResolutionError(key, f'Failed to import module {module_name!r} (error: {exc.__class__.__name__})')

    attr = getattr(module, attr_name, UNDEFINED)
    if attr is UNDEFINED:
        raise SpecResolutionError(key, f'Failed to access {attr!r} from module {module_name!r}')

    return attr
