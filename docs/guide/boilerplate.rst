.. _guide-boilerplate:

.. currentmodule:: prept

Boilerplate Configuration
=========================

Prept provides a range of boilerplate customization options to cater multiple use cases. These
options are discussed in detail on this page.

Configuration File
------------------

Each boilerplate has a configuration file which is generated when the boilerplate is initialized
through the ``prept init`` command. This is the ``preptconfig.json`` file. This file contains
all the options used to customize the boilerplate.

The only required setting right now in this file is ``name`` which represents the name
of with which the boilerplate is referred to while installing.

Boilerplate names must follow these rules:

- Can only contain alphanumeric, underscores, and hyphen characters.
- Must begin with letter or underscore.
- Not case sensitive

The following is a basic preptconfig.json file::

    {
        "name": "basic-boilerplate"
    }

Summary and Version
-------------------

Boilerplate configuration provide two options for specifiying the boilerplate's metadata: ``summary``
and ``version``.

``summary`` is a brief description of boilerplate and ``version`` is the version of boilerplate
and both these options exist to aid commands like ``prept info`` which show information about
a boilerplate.

It is generally a good practice to specify these two parameters if you intend to distribute a
boilerplate for others to use.

Although Prept does not fully supports versioning as of now, ``version`` will be useful in
future when proper versions of boilerplate are supported. Note that version can take version
strings compliant with specification defined in PEP 440: https://peps.python.org/pep-0440/

Ignoring Paths at Generation Time
---------------------------------

You can set ``ignore_path`` option to ignore certain files and directories from being part
of the generated project.

This option takes an array of gitignore-like path patterns as strings.

For example::

    {
        "name": "basic-boilerplate",
        "ignore_paths": [
            ".git/",
            ".vscode/*",
            "!.vscode/settings.json",
            ".env"
        ]
    }

At the generation time, the ``.git`` directory will not be part of generated project
and all content of ``.vscode`` directory will be ignored except ``settings.json``.

Default Generation Directory
----------------------------

``default_generation_directory`` is the name of directory where generated source files
are place if user does not provide any output path through ``-O`` option in prept ``prept new``.

By default, the boilerplate's name is used as ``default_generation_directory`` at generation time.

Note that if the directory does not exist, it will be created.

Templates
---------

Prept provides a simple yet flexible templating system that allows generating files based on
user provided values.

There is a dedicated page covering templates and all the related features in detail. See
the :ref:`guide-templating` page.
