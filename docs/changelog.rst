.. _changelog:
.. currentmodule:: prept

Changelog
=========

v0.2.0
~~~~~~

**Additions**

- Add :attr:`~BoilerplateInfo.variable_input_mode` option to change behaviour of variables input prompt
- Add support for :ref:`template paths <guide-templating--template-paths>`
- Add support for :ref:`dynamic generation <guide-dynamic-generation>`
- Add support for installation of boilerplates from git repositories

**Enhancements and Changes**

- :class:`PreptCLIError` now supports proper indentation formatting of multiline error message and hint
- :meth:`TemplateProvider.render` has been renamed to :meth:`TemplateProvider.process_content`
- :program:`prept info` now shows the basic details (name, required/optional, summary) of template variables
- :attr:`~BoilerplateInfo.template_provider` now takes spec in standard Python module format i.e. ``module:object``
- Output directories created by Prept are now properly cleaned up in case of errors during generation
- ``.git`` directory is now ignored at installation time.

**Fixes**

- Fix :attr:`~BoilerplateInfo.allow_extra_variables` not having any effect
- Fix template provider not resolving through class name when :func:`get_prept_template_provider` function was defined
- Fix resolution failure for template providers from modules present in current working or boilerplate directory

v0.1.0
~~~~~~

Initial release
