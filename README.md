# Prept
Tool for managing and generating boilerplates.

Prept provides interface for managing a collection of boilerplates and bootstrapping projects by
reusing these boilerplates along with the features:

- Intuitive boilerplate installation and management
- Flexible template system with support for custom template providers
- Built-in support for $-substitution and Jinja2 templates
- Extensive customization options to manipulate generation behavior

## Installation
Prept can be installed through pip or another Python package manager:

```sh
$ python -m pip install prept
```

Note that Python 3.9 or a higher version is required for installing Prept.

If you intend to use [Jinja templates](https://jinja.palletsprojects.com/en/stable/),
install through `prept[jinja]` which installs Jinja2 along with Prept.

## Basic Usage
Prept operates on boilerplates which are simply directories containing source
code files that can be reused.

### Initializing & Installing
To show this, below is an example Python web app template in a directory named
`web-app-template`:

```
web-app-template
│
├── routers
│   ├── users.py
│   ├── messages.py
│   └── groups.py
│
├── utils.py
└── main.py
```

We can initialize this directory as a Prept repository by running the ``prept init``
command in this directory::

```sh
$ prept init python-web-app
```

``python-web-app`` is the name of boilerplate that will be used to refer to it when
generating a project from this boilerplate.

This command creates a boilerplate configuration file ``preptconfig.json``:

```
web-app-template
│
├── routers
│   ├── users.py
│   ├── messages.py
│   └── groups.py
│
├── preptconfig.json
├── utils.py
└── main.py
```

![](docs/_assets/prept_init.gif)

We can now globally install boilerplate through `prept install` command:

```
$ prept install .
```

> `.` as argument indicates that boilerplate to be installed is present in the
> current working directory (same directory as preptconfig.json).

![](docs/_assets/prept_install.gif)

### Generating Project

We can now use `prept new` command supplying this boilerplate's name as argument
along with output directory to bootstrap a project from this boilerplate.

```
$ prept new python-web-app -O my-web-app
```

`my-web-app` is the name of output directory where project files are created.

![](docs/_assets/prept_new_installed.gif)

## Templating
Prept provides a simple yet flexible templating system that allows generating boilerplate files
with values provided by user at generation time.

The following is the content of ``main.py`` in the same boilerplate we used in examples
above:

    import flask

    app = flask.Flask(__name__)

    @app.route('GET', '/')
    def index():
        return {'message': 'Welcome to $APP_NAME'}

    if __name__ == '__main__':
        app.run(debug=True)

Here, we are expecting that ``$APP_NAME`` can be replaced with a value that
user can provide at the time of project generation.

We are using ``stringsub`` template provider which provide variable substitutions
using the dollar sign ($) syntax as we used in main.py content above.

We define template provider, files, and variables in preptconfig.json. Here is the
updated configuration::

    {
        "name": "python-web-app",
        "template_provider": "stringsub",
        "template_files": ["main.py"],
        "template_variables": {
            "APP_NAME": {
                "summary": "The name of application.",
                "required": false,
                "default": "Simple Web Application"
            }
        }
    }

As we have updated the boilerplate, we must install it again:

```
prept install .
```

We can now run `prept new` command and provide the value for `APP_NAME` variable
for it to be injected into `main.py`.

```sh
$ prept new python-web-app -O my-app
INFO    Generating project from boilerplate: python-web-app
INFO    No existing directory found. Creating project directory at 'D:\Projects\my-app'
INFO    Successfully created project directory at D:\Projects\my-app
INFO    Processing template variables
OPTION  The name of application.

        APP_NAME (optional) [Simple Web Application]: Chat Application

INFO    Creating project files at 'D:\Projects\my-app'

    ├── Creating my-app\main.py ... DONE
    ├── Applying template on my-app\main.py ... DONE
    ├── Creating my-app\routers\groups.py ... DONE
    ├── Creating my-app\routers\messages.py ... DONE
    ├── Creating my-app\routers\users.py ... DONE
    ├── Creating my-app\utils.py ... DONE

SUCCESS Successfully generated project from 'python-web-app' boilerplate at 'D:\Projects\my-app'
```

![](docs/_assets/prept_new_template.gif)

The generated ``main.py`` in project output directory has the following content:

```
import flask

app = flask.Flask(__name__)

@app.route('GET', '/')
def index():
    return {'message': 'Welcome to Chat Application'}

if __name__ == '__main__':
    app.run(debug=True)
```

As you can see, `$APP_NAME` was replaced with `Chat Application`.

For complex applications, Prept provides templating based on Jinja. See [Templating Guide](https://prept.readthedocs.io/en/latest/guide/templating.html) page in the documentation.

## Documentation
Prept comes with an array of useful features and customization capabilities. Listing them
all here is not possible.

Read the [Prept documentation](https://prept.rtfd.io), specifically the [user guide](https://prept.rtfd.io/en/latest/guide.html) to learn about more features.
