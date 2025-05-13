.. _api-boilerplate-info:

.. currentmodule:: prept

Boilerplate Metadata
====================

Prept boilerplate data is stored in ``preptconfig.json`` file. The classes documented provide a rich interface
to interact with (i.e. read and dynamically manipulate) this file.

.. autoclass:: BoilerplateInfo
    :members:

Template Variables
------------------

Template variables are defined in preptconfig.json and their values are provided at generation time. These
variables are injected into template files by the template providers.

.. autoclass:: TemplateVariable
    :members:
