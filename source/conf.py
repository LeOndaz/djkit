import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# project path
ROOT_PATH = Path(".").resolve().parent.as_posix()
ENV_FILE = (Path(".").resolve() / ".env").parent.as_posix()

load_dotenv(ENV_FILE)

sys.path.insert(0, ROOT_PATH)

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "drf-common"
copyright = "2023, LeOndaz"
author = "LeOndaz"
release = "1.0.4"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc"]

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]
