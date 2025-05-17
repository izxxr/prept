# Copyright (C) Izhar Ahmad 2025-2026

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar
from types import ModuleType
from prept.errors import TemplateProviderNotFound, InvalidConfig, PreptCLIError

import string
import sys
import pathlib
import importlib.util
import importlib.machinery

try:
    import jinja2
except ImportError:
    jinja2 = None

_JINJA2_INSTALLED = jinja2 is not None

if TYPE_CHECKING:
    from prept.context import GenerationContext
    from prept.file import BoilerplateFile

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

    Packages providing custom template providers should define
    this function at module level. Prept will call this function
    at generation time with the provider name from preptconfig.json.

    This function should return a subclass of :class:`TemplateProvider`
    or ``None`` if provider name is invalid.

    Parameters
    ~~~~~~~~~~
    name: :class:`str`
        The provider's name.

    Returns
    ~~~~~~~
    type[:class:`TemplateProvider`]
        The template provider resolved from given name.
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
        The resolved template provider.
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

    Template providers are "middleware" classes that process the content
    of template files at generation time and inject the values of template
    variables.

    All template providers, external or provided by Prept, inherit from
    this class and implement the :meth:`.process_content` and :meth:`.process_path`
    methods. All providers must also set the :attr:`.name` class attribute.

    Prept provides the following built-in template providers:

    - :class:`StringTemplateProvider` for $-substitutions based templating
    - :class:`Jinja2TemplateProvider` for Jinja templates (requires Jinja2 installed)

    Attributes
    ~~~~~~~~~~
    name: :class:`str`
        Class attribute.

        The name used to identify the template provider.
    """
    name: ClassVar[str]

    # This marker is used to check if given template provider inherits
    # from this base TemplateProvider class. Because resolve_template_provider()
    # uses importlib to load module from spec, issubclass() helper does not work
    # properly due to separate class objects being created.
    # See this SO question: https://stackoverflow.com/q/11461356
    __prept_template_provider__ = True

    def process_path(self, path: pathlib.Path, context: GenerationContext) -> pathlib.Path:
        """"Processes the given path and replaces the.

        This returns the :class:`pathlib.Path` object representing
        the processed path.

        Parameters
        ~~~~~~~~~~
        path: :class:`pathlib.Path`
            The path to process.
        context: :class:`GenerationContext`
            The generation context containing generation time information.
        """
        raise NotImplementedError

    def process_content(self, file: BoilerplateFile, context: GenerationContext) -> str | bytes:
        """Processes the file content and inject variables into it.

        This returns the processed file content generated from template
        in textual (string) or binary (bytes) format.

        Parameters
        ~~~~~~~~~~
        file: :class:`BoilerplateFile`
            The file to be processed.
        context: :class:`GenerationContext`
            The generation context containing generation time information.
        """
        raise NotImplementedError


class StringTemplateProvider(TemplateProvider):
    """$-substitutions based templates by :class:`string.Template`.

    This uses :meth:`string.Template.safe_substitute()` to ensure that any invalid
    or missing variables are silently ignored at generation time.

    This is identified by the ``stringsub`` name.
    """

    name = 'stringsub'

    def process_path(self, path: pathlib.Path, context: GenerationContext) -> pathlib.Path:
        updated = string.Template(str(path)).safe_substitute(context.variables)
        return pathlib.Path(updated)

    def process_content(self, file: BoilerplateFile, context: GenerationContext) -> str | bytes:
        content = file.read()
        return string.Template(content).safe_substitute(context.variables)


class Jinja2TemplateProvider(TemplateProvider):
    """Provider based on Jinja2 templates.

    This template provider requires Jinja2 to be installed.

    Jinja templates are commonly used for HTML files in web frameworks such
    as Flask. However, it can be used for any kind of source file.

    The following is an example of Jinja template HTML file (taken directly
    from Jinja2 documentation):

    .. code-block:: html

        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>My Webpage</title>
        </head>
        <body>
            <ul id="navigation">
            {% for item in navigation %}
                <li><a href="{{ item.href }}">{{ item.caption }}</a></li>
            {% endfor %}
            </ul>

            <h1>My Webpage</h1>
            {{ a_variable }}

            {# a comment #}
        </body>
        </html>

    For more information, please refer to Jinja documentation: https://jinja.palletsprojects.com/

    This is identified by the ``jinja2`` name.
    """

    name = 'jinja2'

    def process_path(self, path: pathlib.Path, context: GenerationContext) -> pathlib.Path:
        assert jinja2 is not None  # this never fails
        temp = jinja2.Template(str(path))

        return pathlib.Path(temp.render(context.variables))

    def process_content(self, file: BoilerplateFile, context: GenerationContext) -> str | bytes:
        assert jinja2 is not None
        
        src = file.read()
        temp = jinja2.Template(src)
        
        return temp.render(context.variables)
