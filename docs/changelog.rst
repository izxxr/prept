.. _changelog:
.. currentmodule:: prept

Changelog
=========

v0.2.0
~~~~~~

**Additions**

- Add :attr:`~BoilerplateInfo.variable_input_mode` option to change behaviour of variables input prompt
- Add support for :ref:`template paths <guide-templating--template-paths>`

**Enhancements and Changes**

- :class:`PreptCLIError` now supports proper indentation formatting of multiline error message and hint
- :meth:`TemplateProvider.render` has been renamed to :meth:`TemplateProvider.process_content`
- :program:`prept info` now shows the basic details (name, required/optional, summary) of template variables

**Fixes**

- Fix :attr:`~BoilerplateInfo.allow_extra_variables` not having any effect

v0.1.0
~~~~~~

Initial release
