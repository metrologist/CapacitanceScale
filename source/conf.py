# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import sys
# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Capacitance Scale'
copyright = '2026, Keith Jones'
author = 'Keith Jones'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

sys.path.insert(0, os.path.abspath(r'C:\Users\k.jones\OneDrive - Callaghan Innovation\KJ\PycharmProjects\CapacitanceScale'))

extensions = ['sphinx.ext.autodoc'
              ]
autodoc_default_options = {'special-members': '__init__', 'autoclass-content': 'both'}

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinxdoc'
html_static_path = ['_static']
