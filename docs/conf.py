"""Sphinx configuration."""

import os
import sys

import tomli

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "NOVA Application Development"
copyright = "2025, ORNL"
author = "John Duggan"
with open("../pyproject.toml", "rb") as toml_file:
    toml_dict = tomli.load(toml_file)
    release = toml_dict["project"]["version"]

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

sys.path.insert(0, os.path.abspath("../src/nova/trame"))

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon", "sphinx_rtd_theme"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
