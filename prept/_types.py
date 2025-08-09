# Copyright (C) Izhar Ahmad 2025-2026

from __future__ import annotations

from typing import Any
from typing_extensions import TypedDict

__all__ = (
    'TemplateProviderOptions',
    'TemplateProviderConfig',
)


class _OptionalProviderOptions(TypedDict, total=False):
    settings: dict[str, Any]


class TemplateProviderOptions(_OptionalProviderOptions):
    name: str


TemplateProviderConfig = str | TemplateProviderOptions | None
