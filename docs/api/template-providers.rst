.. _api-template-providers:

.. currentmodule:: prept

Template Providers
==================

This page documents the machinery behind template providers, the middleware that process the template files
and inject template variables into them.

.. autoclass:: TemplateProvider
    :members:

Built-in Providers
------------------

Prept provides the following template providers built-in to cater common use cases. Support for more template
providers will be added in future.

StringTemplateProvider
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: StringTemplateProvider
    :members:


Jinja2TemplateProvider
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: Jinja2TemplateProvider
    :members:

Provider Resolution
-------------------

Prept provides an interface to define custom template providers. This interface also allows third party packages
and libraries to implement and distribute template providers that can be used directly by installing them and
referring to them in configuration file.

.. autofunction:: get_prept_template_provider

.. autofunction:: resolve_template_provider
