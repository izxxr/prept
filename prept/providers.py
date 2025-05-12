# Copyright (C) Izhar Ahmad 2025-2026

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar
from types import ModuleType
from prept.context import GenerationContext
from prept.errors import TemplateProviderNotFound, InvalidConfig, PreptCLIError

import string
import sys
import importlib.util
import importlib.machinery

try:
    import jinja2
except ImportError:
    jinja2 = None

_JINJA2_INSTALLED = jinja2 is not None

if TYPE_CHECKING:
    from prept.context import GenerationContext

__all__ = (
    'resolve_template_provider',
    'get_prept_template_provider',
    'TemplateProvider',
    'StringTemplateProvider',
    'Jinja2TemplateProvider',
)


def _load_module_from_spec(spec: importlib.machinery.ModuleSpec, mod_name: str) -> ModuleType:
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    assert spec.loader is not None

    try:
        spec.loader.exec_module(module)
    except Exception as e:
        del sys.modules[mod_name]
        raise RuntimeError from e  # for wrapping purposes
    else:
        return module


def get_prept_template_provider(name: str) -> type[TemplateProvider] | None:
    """Prept's default template provider resolver.

    Packages providing custom template providers should
    define a similar function.

    Parameters
    ~~~~~~~~~~
    name: :class:`str`
        The provider's name.
    """
    if name == StringTemplateProvider.name:
        return StringTemplateProvider

    if name == Jinja2TemplateProvider.name:
        if not _JINJA2_INSTALLED:
            raise PreptCLIError(
                'Jinja must be installed in order to use the "jinja2" template provider. ',
                hint='See https://jinja.palletsprojects.com/en/stable/intro/#installation for help on installing Jinja2'
            )

        return Jinja2TemplateProvider

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
        raise InvalidConfig('template_provider', 'Template provider name cannot be empty')

    if len(parts) == 1:
        package = 'prept.providers'
        provider_name = parts[0]
    elif len(parts) == 2:
        package, provider_name = parts
        package = package.strip()
        provider_name = provider_name.strip()
    else:
        raise TemplateProviderNotFound(name, 'too many separators')

    if not package:
        package = 'prept.providers'
    if not provider_name:
        raise TemplateProviderNotFound(name, 'no provider name given')

    spec = importlib.util.find_spec(package)
    if spec is None:
        raise TemplateProviderNotFound(name, f'could not find module {package!r}') from None

    try:
        module = _load_module_from_spec(spec, package.strip())
    except RuntimeError:
        raise TemplateProviderNotFound(name, f'could not load module {package!r}') from None

    resolver = getattr(module, 'get_prept_template_provider', None)
    if resolver is None:
        provider = getattr(module, provider_name.strip(), None)
    else:
        try:
            provider = resolver(provider_name)
        except Exception as e:
            if isinstance(e, PreptCLIError):
                raise

            raise TemplateProviderNotFound(name, f'error in resolution: {e}') from None

    if provider is None:
        raise TemplateProviderNotFound(name, 'failed to resolve')

    if not getattr(provider, '__prept_template_provider__', False):
        raise TemplateProviderNotFound(name, f'not a subclass of TemplateProvider; found {provider!r}')

    return provider


class TemplateProvider:
    """Base class for all template providers.

    All template providers, external or provided by Prept, inherit from
    this class and implement the :meth:`.render` method. All providers
    must also set the name class attribute.
    """
    name: ClassVar[str]

    # This marker is used to check if given template provider inherits
    # from this base TemplateProvider class. Because resolve_template_provider()
    # uses importlib to load module from spec, issubclass() helper does not work
    # properly due to separate class objects being created.
    # See this SO question: https://stackoverflow.com/q/11461356
    __prept_template_provider__ = True

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

    name = 'string-sub'

    def render(self, context: GenerationContext) -> str:
        content = context.current_file.read()
        return string.Template(content).safe_substitute(context.variables)


class Jinja2TemplateProvider(TemplateProvider):
    """Provider based on Jinja2 templating."""

    name = 'jinja2'

    def render(self, context: GenerationContext) -> str | bytes:
        assert jinja2 is not None  # this never fails
        
        src = context.current_file.read()
        temp = jinja2.Template(src)
        
        return temp.render(context.variables)
