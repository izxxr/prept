# Copyright (C) Izhar Ahmad 2025-2026

from __future__ import annotations

from typing import Any

import os
import stat
import errno

__all__ = (
    'handle_rm_read_only',
)

# This is adapted from https://stackoverflow.com/a/1214935
def handle_rm_read_only(func: Any, path: str, exc: BaseException):
    """Exception handler for shutils.rmtree()
    
    Handles failed file deletions due to permissions error.
    """
    if not isinstance(exc, PermissionError):
        raise
    if func in (os.rmdir, os.remove, os.unlink) and exc.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO) # 0777
        func(path)
    else:
        raise
