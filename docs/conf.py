# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

sys.path.insert(0, os.path.abspath('../'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Prept'
copyright = '2025, Izhar Ahmad'
author = 'Izhar Ahmad'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_click',
]

templates_path = ['_templates']
exclude_patterns = []
html_sidebars = {"cli": []}  # type: ignore


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = ['_static']

html_theme_options = {
    "github_url": "https://github.com/izxxr/prept",
    "show_toc_level": 4,
}

# Autodoc
autodoc_member_order = 'bysource'
autodoc_inherit_docstrings = False
