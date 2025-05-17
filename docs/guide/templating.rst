.. _guide-templating:

.. currentmodule:: prept

Templating
==========

Prept provides a simple yet flexible templating system that allows generating boilerplate files
with values provided by user at generation time.

Terminologies
-------------

There are a few terms that Prept uses related to templates:

- **Template Variables:** variables whose values are provided by user at generation time

- **Template Provider:** a middleware that processes template files and injects variable values.

- **Template Files:** the files in which variable values are to be injected.

Basic Usage
-----------

This small subsection quickly showcases how templating is performed. Check example shown on :ref:`guide-quickstart`
page as well for more detailed understanding.

.. _guide-templating--basic-usage--defining-providers:

Defining Providers
~~~~~~~~~~~~~~~~~~

Boilerplates must define a template provider using the :attr:`~BoilerplateInfo.template_provider` option in
configuration file as shown::

    {
        "name": "basic-boilerplate",
        "template_provider": "stringsub"
    }

This defines :class:`StringTemplateProvider` to be used as template provider which uses dollar sign
syntax for variable substitutions.

.. _guide-templating--basic-usage--defining-variables:

Defining Variables
~~~~~~~~~~~~~~~~~~

Template variables are defined through the ``template_variables`` option in configuration file and their
values are provided by user at the generation time.

This option takes a mapping with key being the variable name and value representing the information about
that variable.

For example, the following configuration defines a single template variable ``APP_NAME``::

    {
        "name": "basic-boilerplate",
        "template_provider": "stringsub",
        "template_variables": {
            "APP_NAME": {
                "summary": "The name of application."
            }
        }
    }

:attr:`~TemplateVariable.summary` is the description of variable. It is not required to supply this option but is
recommended to be set as it is displayed at the time of generation and can contain useful information about the variable.

Defining Files
~~~~~~~~~~~~~~

:attr:`~BoilerplateInfo.template_files` is an array of gitignore-like file patterns that define the files that are
regarded as "template." These files are sent to template provider at generation time for variables injection.

For example::

    {
        "name": "basic-boilerplate",
        "template_provider": "stringsub",
        "template_variables": {
            "APP_NAME": {
                "summary": "The name of application.",
                "required": true
            }
        },
        "template_files": [
            "core/*",
            "main.py"
        ]
    }

This defines all files in ``src`` directory as template along with the main.py file as well.

Generating Project
~~~~~~~~~~~~~~~~~~

With the configuration shown above, we can run :program:`prept new` and we will be prompted to enter the
value of ``APP_NAME`` variable. Input value will be injected into the template files in generated project.

.. code-block:: text

    $ prept new basic-boilerplate -O my-app
    INFO    Generating project from boilerplate: basic-boilerplate
    INFO    No existing directory found. Creating project directory at 'D:\Projects\my-app'
    INFO    Successfully created project directory at D:\Projects\my-app
    INFO    Processing template variables
    OPTION  The name of application.

            APP_NAME (required): Chat Application

    INFO    Creating project files at 'D:\Projects\my-app'

        ├── Creating my-app\main.py ... DONE
        ├── Applying template on my-app\main.py ... DONE
        ├── Creating my-app\routers\groups.py ... DONE
        ├── Creating my-app\routers\messages.py ... DONE
        ├── Creating my-app\routers\users.py ... DONE
        ├── Creating my-app\core\utils.py ... DONE
        ├── Applying template on my-app\core\utils.py ... DONE

    SUCCESS Successfully generated project from 'basic-boilerplate' boilerplate at 'D:\Projects\my-app'

Alternatively, we can pass the value of variables through :option:`prept new -V` or :option:`prept new --var`
option which takes two values: the variable name and its value. For example::

    $ prept new basic-boilerplate -O ./basic_project -V APP_NAME "Chat Application"

Template Providers
------------------

Template provider is a simple middleware function (class) that is called by Prept and it processes the
template file's content, injecting the variable values into it.

Typically, variable values are injected into file content by template provider through some templating
language (like Jinja, as by :class:`Jinja2TemplateProvider`).

Built-in Providers
~~~~~~~~~~~~~~~~~~

Prept provides two built-in template providers:

- ``stringsub`` (:class:`StringTemplateProvider`) based on $-substitutions
- ``jinja2`` (:class:`Jinja2TemplateProvider`) based on Jinja templates

Provider Name
~~~~~~~~~~~~~

As shown in :ref:`guide-templating--basic-usage--defining-providers`, template providers are defined
using the :attr:`~BoilerplateInfo.template_provider` option. It takes the name of a template provider
in either of the following formats:

- ``provider_name``
- ``provider_class``
- ``package::provider_name``
- ``package::provider_class``

``provider_name`` is the name of template provider such as ``stringsub`` for :class:`StringTemplateProvider`
and ``provider_class`` is the name of template provider class such as ``StringTemplateProvider``. For example::

    {
        "name": "basic-boilerplate",
        "template_provider": "stringsub"
    }

``package`` is simply the name of a Python package or module. When using third party or custom template providers,
they must referred by including the package name as well that provides the template provider separating the package
name and provider name/class with double colon ``::``.

For example::
    
    {
        "name": "basic-boilerplate",
        "template_provider": "foobar::simpletemp"
    }

will resolve to ``simpletemp`` template provider from ``foobar`` package or module.

.. note::
    
    The provider name or class name is passed to package's :func:`get_prept_template_provider` resolver
    function which returns the template provider that is called by Prept.

    More detail on defining custom template providers and this resolver function will be covered
    in a later section.

Template Variables
------------------

Template variables are variables whose values (provided at generation time) are injected by template provider
into template files.

Variable Name
~~~~~~~~~~~~~

Variable names must pass the following set of rules:

- Can only contain alphanumeric and underscores characters.
- Must begin with letter or underscore.
- Case sensitive

Variable Summary
~~~~~~~~~~~~~~~~~

:ref:`guide-templating--basic-usage--defining-variables` describes how variables are defined through the
``template_variable`` option which takes a mapping whose values describe the variable.

Each variable can take an optional :attr:`~TemplateVariable.summary` option which is the brief description
of variable. This description is shown at the time of generation and can contain useful information about
the variable.

.. code-block:: js

    {
        "template_variables": {
            "APP_NAME": {
                "summary": "The name of application."  // displayed at generation time
            }
        }
    }

Required and Optional Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, all template variables are required. That is, their values must be provided by user at
generation time.

It is possible to declare optional variables whose values may be omitted. This is acheived at
through :attr:`~TemplateVariable.required` option (true by default).

.. code-block:: js

    {
        "template_variables": {
            "APP_NAME": {
                "required": false  // optional variable
            }
        }
    }

Optional variables without any default are given no value at generation time. More specifically,
their values are not present in the :attr:`GenerationContext.variables` mapping which is used
to inject variables into template files.

Default Values
~~~~~~~~~~~~~~

Optional variables can be given a "default" value which is assigned to variable if it is
not provided. For example:

.. code-block:: js

    {
        "template_variables": {
            "APP_NAME": {
                "default": "Web App"
            }
        }
    }


Note that whenever a default is set, the value set for :attr:`~TemplateVariable.required` is implicitly
determined as ``false`` regardless of the value set to it. Variable with defaults are always optional.

Arbitrary Variables
~~~~~~~~~~~~~~~~~~~

By default, Prept forbids passing invalid variables through the :option:`prept new -V` option. However, this
can be allowed by setting :attr:`~BoilerplateInfo.allow_extra_variables` to true on boilerplate
configuration.

.. code-block:: js

    {
        "template_variables": {
            "APP_NAME": {
                "summary": "The application name"
            }
        },
        "allow_extra_variables": true  // allows arbitrary variables through -V option
    }

The extra variables' values are added to the :attr:`GenerationContext.variables` mapping used
for injecting variable values into template files.

Variables Input
~~~~~~~~~~~~~~~

There are two modes of providing variable while generating boilerplates: through the :option:`prept new -V` option, or through
the input prompts in :program:`prept new` command output.

By default, Prept will prompt the user to input variables that were not provided through the :option:`prept new -V` option. This
behaviour can be changed using the ``variable_input_mode`` setting. It can take three values:

- ``all`` (default)
- ``required_only``
- ``none``

``all`` is the default value and with this set, Prept will prompt the user to input all variables that
were not provided by :option:`prept new -V` option regardless of whether the variable is required or not.

With ``required_only``, the user is prompted to only input the required variables. Optional variables
can only be set through :option:`prept new -V` option.

``none`` completely disables variables input prompt. With this setting, all variable values should
be provided through :option:`prept new -V` option. If there are required variables, they must be provided
using :option:`prept new -V` otherwise an error is raised by :program:`prept prept new`.
