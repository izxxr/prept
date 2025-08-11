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
