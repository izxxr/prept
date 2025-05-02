# Copyright (C) Izhar Ahmad 2025-2026

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar
from prept.errors import TemplateProviderNotFound

import string
import importlib

if TYPE_CHECKING:
    from prept.context import GenerationContext

__all__ = (
    'resolve_template_provider',
    'get_prept_template_provider',
    'TemplateProvider',
    'StringTemplateProvider',
)


def get_prept_template_provider(name: str) -> type[TemplateProvider] | None:
    """Prept's default template provider resolver.

    Packages providing custom template providers should
    define a similar function.

    Parameters
    ~~~~~~~~~~
    name: :class:`str`
        The provider's name.
    """
    if name == 'string-template':
        return StringTemplateProvider

    return None


def resolve_template_provider(name: str) -> type[TemplateProvider]:
    """Resolves a template provider from its name.

    The name is given in one the following format:

    - ``provider-name``
    - ``provider-class-name``
    - ``package::provider-name``
    - ``package::provider-class-name``

    If no ``package`` is provided, it is assumed that a built-in
    template provider from Prept is needed.

    The ``provider-name`` is the :attr:`TemplateProvider.name` attribute
    of template provider and if provided, the provider is resolved through
    the :func:`get_prept_template_provider` function defined by the package.

    If ``provider-name`` resolution fails, ``provider-class-name`` resolution
    is performed.

    Returns
    ~~~~~~~
    type[:class:`TemplateProvider`]
    """
    parts = name.split("::")
    if not parts:
        raise TemplateProviderNotFound(name)

    if len(parts) == 1:
        package = 'prept.providers'
        provider_name = parts[0]
    elif len(parts) == 2:
        package, provider_name = parts
    else:
        raise TemplateProviderNotFound(name)

    if not package:
        package = 'prept.providers'
    if not provider_name:
        raise TemplateProviderNotFound(name)

    try:
        module = importlib.import_module(package.strip())
    except ImportError:
        raise TemplateProviderNotFound(name) from None

    resolver = getattr(module, 'get_prept_template_provider', None)
    if resolver is None:
        provider = getattr(module, provider_name.strip(), None)
    else:
        try:
            provider = resolver(provider_name)
        except Exception:
            raise TemplateProviderNotFound(name) from None
        
    if provider is None:
        raise TemplateProviderNotFound(name)
    
    return provider


class TemplateProvider:
    """Base class for all template providers.

    All template providers, external or provided by Prept, inherit from
    this class and implement the :meth:`.render` method. All providers
    must also set the name class attribute.
    """

    name: ClassVar[str]

    def render(self, context: GenerationContext) -> str | bytes:
        """Renders the template.

        This returns the file content generated from template in
        textual (string) or binary (bytes) format.

        Parameters
        ~~~~~~~~~~
        context: :class:`GenerationContext`
            The generation context containing generation-time and file information.
        """
        raise NotImplementedError


class StringTemplateProvider(TemplateProvider):
    """$-substitutions based templating by :class:`string.Template`.

    This uses :meth:`string.Template.safe_substitute()` to ensure that any invalid
    or missing variables are silently ignored at render time.
    """

    name = "string-template"

    def render(self, context: GenerationContext) -> str:
        content = context.current_file.read()
        return string.Template(content).safe_substitute(context.variables)
