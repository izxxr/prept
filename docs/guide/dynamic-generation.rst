.. _guide-dynamic-generation:

.. currentmodule:: prept

Dynamic Generation
==================

Prept provides a rich Python API for manipulating generation behavior dynamically at generation time. The useful
bits of this feature are presented on this page.

Generation Engine
-----------------

Generation engine, represented by :class:`GenerationEngine`, is a class that provides the interface and
tools for facilitating dynamic generation.

Currently, generation engine only provides file processors which are functions that are called by Prept
when a certain file is being generated and these functions can control the generation of file.

Defining Engine
~~~~~~~~~~~~~~~

Generation engine is typically defined in a Python file present in boilerplate directory. We
can simply call this file ``gen_engine.py`` and a file is shown below::

    import prept

    engine = prept.GenerationEngine()

    @engine.processor('src/utils.py')
    def process_utils(ctx):
        print('Processing utils.py')

``engine`` here is :class:`GenerationEngine` instance and currently, this engine currently
defines a :ref:`file processor <guide-dynamic-generation--file-processors>` which simply
prints a message when utils.py is being generated, nothing else.

In order to actually put this engine into use, Prept needs to know "where" the engine is located
and we define this using the :attr:`~BoilerplateInfo.engine` setting in preptconfig.json::

    {
        "name": "basic-boilerplate",
        "engine": "gen_engine:engine",
        "ignore_paths": ["gen_engine.py"]
    }

Here, :attr:`~BoilerplateInfo.engine` takes the Python module spec in which the name of module
in which engine is present and the name of variable that contains engine object is separated by
a colon.

Normally, we don't want our engine definition to be part of the projects that are generated from
the boilerplate so we add ``gen_engine.py`` to :attr:`BoilerplateInfo.ignore_paths` array.

Now, when we run ``prept new basic-boilerplate``, we see a ``Processing utils.py`` message when the
``src/utils.py`` file is being generated.

.. code-block:: sh

    $ prept new basic-boilerplate -O my-app
    INFO    Generating project from boilerplate: basic-boilerplate
    INFO    No existing directory found. Creating project directory at 'D:\Projects\my-app'
    INFO    Successfully created project directory at D:\Projects\my-app
    INFO    Processing template variables
    INFO    Creating project files at 'D:\Projects\my-app'

        ├── Creating my-app\main.py ... DONE
        ├── Creating my-app\routers\groups.py ... DONE
        ├── Creating my-app\routers\messages.py ... DONE
        ├── Creating my-app\routers\users.py ... DONE
    Processing utils.py
        ├── Creating my-app\core\utils.py ... DONE

    SUCCESS Successfully generated project from 'basic-boilerplate' boilerplate at 'D:\Projects\my-app'

.. _guide-dynamic-generation--file-processors:

File Processors
---------------

File processors are functions that are defined for specific file or multiple files that are called when
those file(s) are being generated. These functions are normally useful in manipulating the generation
behavior of specific files.

File processors are typically defined through the :meth:`Engine.processor` decorator as shown in the following
example::

    import prept

    engine = prept.GenerationEngine()

    @engine.processor('src/utils.py')
    def process_utils(ctx):
        print('Processing utils.py')

This processor does nothing functionally but only prints a message when ``src/utils.py`` is being generated.

Return Value
~~~~~~~~~~~~

A common use case of file processor is also controlling whether a file should be generated or not. For example,
sometimes you want to generate a file based on some template variable's value.

Processors can return a boolean to indicate file generation status:

- If a processor returns ``True``, the file is generated normally.
- If a processor returns ``False``, the file is not generated.
- If a processor returns nothing (or ``None``), it is implicitly regarded as ``True`` and file is generated.


To demonstrate, consider the following boilerplate directory structure and configuration::

    python-web-app
    │
    ├── src
    │   │
    │   ├── routers
    │   │   ├── users.py
    │   │   ├── messages.py
    │   │   └── groups.py
    │   │
    │   └── utils.py
    │
    ├── preptconfig.json
    ├── gen_engine.py
    └── main.py

The content of preptconfig.json::

    {
        "name": "python-web-app",
        "ignore_paths": ["gen_engine.py"],
        "engine": "gen_engine:engine",
        "template_variables": {
            "INCLUDE_UTILS": {
                "summary": "Whether to include utility files or not (y/N)"
            }
        }
    }

Our engine and file processor definition in ``gen_engine.py`` is as follows::

    import prept

    engine = prept.GenerationEngine()

    @engine.processor('src/utils.py')
    def process_utils(ctx):
        value = ctx.variables['INCLUDE_UTILS'].lower()
        if value == 'y':
            return True  # generate utils.py
        if value == 'n':
            return False  # do not generate utils.py
        
        # invalid input other than y or n
        raise prept.PreptCLIError('Invalid choice! Allowed choices were "y" or "N"')

Here, we are defining a file processor that processes the generation of ``src/utils.py`` file.

.. note::

    Note that the string passed to :meth:`~GenerationEngine.processor` decorator
    can be any valid gitignore-like path pattern. This allows us to define single
    processor for an entire directory.

    For example, ``engine.processor('src/*')`` will be used for defining a processor
    that processes all files in the src directory.

We are checking the value of ``INCLUDE_UTILS`` and depending on this value, we are
returning true or false to indicate whether the file should be generated or not.

Inputting ``Y`` for ``INCLUDE_UTILS`` would result in ``utils.py`` to generate properly. In
case of passing ``N`` to this variable, ``utils.py`` will not be generated and will not be
part of output directory as shown below.

.. note::

    If choice is neither ``Y`` or ``n``, we are raising :class:`PreptCLIError` which is
    automatically catched and propagated (or formatted) as proper error output by Prept.

.. code-block:: sh

    $ prept new basic-boilerplate -O my-app
    INFO    Generating project from boilerplate: basic-boilerplate
    INFO    No existing directory found. Creating project directory at 'D:\Projects\my-app'
    INFO    Successfully created project directory at D:\Projects\my-app
    INFO    Processing template variables
    OPTION  Whether to include utility files or not (y/N)

        INCLUDE_UTILS (required): N

    INFO    Creating project files at 'D:\Projects\my-app'

        ├── Creating my-app\main.py ... DONE
        ├── Creating my-app\routers\groups.py ... DONE
        ├── Creating my-app\routers\messages.py ... DONE
        ├── Creating my-app\routers\users.py ... DONE
        ├── Skipping generation of my-app\core\utils.py (processor signal)

    SUCCESS Successfully generated project from 'basic-boilerplate' boilerplate at 'D:\Projects\my-app'

The second last line in the output above shows that utils.py was not generated and this can be seen
in output directory as well which does not contain this file in ``src`` directory::

    my-app
    │
    ├── src
    │   │
    │   ├── routers
    │   │   ├── users.py
    │   │   ├── messages.py
    │   │   └── groups.py
    │
    └── main.py

Hooks
-----

Hooks are functions that are called at specific points in generation process.

Pre-generation Hook
~~~~~~~~~~~~~~~~~~~

Pre-generation hook is called before any files are generated and after initialization is done (i.e. variables have
been processed). This hook is useful in performing any initial setup.

:meth:`GenerationEngine.pre_generation_hook` decorator is used to register pre-generation hook and the decorated
function takes a single :class:`GenerationContext` instance as parameter::

    engine = prept.GenerationEngine()

    @engine.pre_generation_hook
    def setup(ctx):
        print("Call pre-generation hook!")

.. note::

    A few things to note:

    - In pre-generation hook, accessing :attr:`GenerationContext.current_file` property will raise
      a runtime error as no file is being generated at that point.

    - :attr:`GenerationContext.variables` is guaranteed to be filled in pre-generation hook as this
      hook is called *after* variables have been processed so it is possible to perform any preprocessing
      based on variable values.

    - Any :class:`PreptCLIError` error raised in pre-generation hook is formatted and output properly.

Post-generation Hook
~~~~~~~~~~~~~~~~~~~~

This hook is called when all files have been generated successfully and is useful for clean up purposes.

:meth:`GenerationEngine.post_generation_hook` decorator is used to register post-generation hook and the
decorated function takes a single :class:`GenerationContext` instance as parameter::

    engine = prept.GenerationEngine()

    @engine.post_generation_hook
    def cleanup(ctx):
        print("Generation all done!")

.. note::

    - In post-generation hook, :attr:`GenerationContext.current_file` points to the last file
      that was generated.

    - Any :class:`PreptCLIError` error raised is formatted and output properly.
