# Copyright (C) Izhar Ahmad 2025-2026

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from prept.errors import InvalidConfig, SpecResolutionError, PreptCLIError
from prept import utils

import string
import pathlib

try:
    import jinja2
except ImportError:
    jinja2 = None

_JINJA2_INSTALLED = jinja2 is not None

if TYPE_CHECKING:
    from prept.context import GenerationContext
    from prept.file import BoilerplateFile

__all__ = (
    'TemplateProvider',
    'StringTemplateProvider',
    'Jinja2TemplateProvider',
)


class TemplateProvider:
    """Base class for all template providers.

    Template providers are "middleware" classes that process the content
    of template files at generation time and inject the values of template
    variables.

    All template providers, external or provided by Prept, inherit from
    this class and implement the :meth:`.process_content` and :meth:`.process_path`
    methods.

    Prept provides the following built-in template providers:

    - :class:`StringTemplateProvider` for $-substitutions based templating
    - :class:`Jinja2TemplateProvider` for Jinja templates (requires Jinja2 installed)

    Attributes
    ~~~~~~~~~~
    settings:
        Dictionary containing settings for provider from preptconfig.json.

        .. versionadded:: 0.4.0
    """

    # This marker is used to check if given template provider inherits
    # from this base TemplateProvider class. Because TemplateProvider._resolve()
    # uses importlib to load module from spec, issubclass() helper does not work
    # properly due to separate class objects being created.
    # See this SO question: https://stackoverflow.com/q/11461356
    __prept_template_provider__ = True

    def __init__(self, settings: dict[str, Any]) -> None:
        self.settings = settings

    @classmethod
    def _resolve(cls, spec: str, key: str = 'template_provider') -> type[TemplateProvider]:
        parts = spec.split(":")
        if not parts:
            raise InvalidConfig(key, 'Template provider name cannot be empty')

        if len(parts) == 1:
            if parts[0] not in BUILT_IN_PROVIDERS:
                raise InvalidConfig(key, f'No built-in provider with name {parts[0]!r} found')

            provider = BUILT_IN_PROVIDERS[parts[0]]
        else:
            provider = utils.resolve_from_module_spec_format(spec, key)

        if not getattr(provider, '__prept_template_provider__', False):
            raise SpecResolutionError(key, f'Provider is not a subclass of TemplateProvider')

        provider._on_provider_resolve()
        return provider

    @classmethod
    def _on_provider_resolve(cls) -> None:
        # XXX: Make this public?
        # Currently, this is used by jinja2 provider (or any future provider requiring
        # an external dependency) to check if the dependency is installed.
        pass

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

    This can be used by setting :attr:`~Boilerplate.template_provider` to ``stringsub``
    """

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

    This can be used by setting :attr:`~Boilerplate.template_provider` to ``jinja2``
    """

    @classmethod
    def _on_provider_resolve(cls) -> None:
        if not _JINJA2_INSTALLED:
            raise PreptCLIError(
                'Jinja must be installed in order to use the "jinja2" template provider. ',
                hint='See https://jinja.palletsprojects.com/en/stable/intro/#installation for help on installing Jinja2'
            )

    def process_path(self, path: pathlib.Path, context: GenerationContext) -> pathlib.Path:
        # get_template_provider() checks Jinja installation so this assertion
        # never fails under normal circumstances. It's here regardless to
        # satisfy type checker.
        assert jinja2 is not None
        temp = jinja2.Template(str(path))

        return pathlib.Path(temp.render(context.variables))

    def process_content(self, file: BoilerplateFile, context: GenerationContext) -> str | bytes:
        assert jinja2 is not None
        
        src = file.read()
        temp = jinja2.Template(src)
        
        return temp.render(context.variables)


BUILT_IN_PROVIDERS = {
    'stringsub': StringTemplateProvider,
    'jinja2': Jinja2TemplateProvider,
}
