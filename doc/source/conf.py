"""Sphinx documentation configuration file."""

from datetime import datetime
import os
from pathlib import Path
import subprocess

from ansys_sphinx_theme import (
    ansys_favicon,
    get_version_match,
)

from ansys.scade.wux import __version__

# Project information
project = 'ansys-scade-wux'
copyright = f'(c) {datetime.now().year} ANSYS, Inc. All rights reserved'
author = 'ANSYS, Inc.'
release = version = __version__
switcher_version = get_version_match(version)

# Select desired logo, theme, and declare the html title
html_theme = 'ansys_sphinx_theme'
html_short_title = html_title = 'Ansys SCADE Wrapper Tools'

# multi-version documentation
cname = os.getenv('DOCUMENTATION_CNAME', 'wux.scade.docs.pyansys.com')
"""The canonical name of the webpage hosting the documentation."""

# specify the location of your github repo
html_theme_options = {
    'github_url': 'https://github.com/ansys/scade-wux',
    'show_prev_next': False,
    'show_breadcrumbs': True,
    'additional_breadcrumbs': [
        ('PyAnsys', 'https://docs.pyansys.com/'),
    ],
    'switcher': {
        'json_url': f'https://{cname}/versions.json',
        'version_match': switcher_version,
    },
    'check_switcher': False,
    'logo': 'pyansys',
    'ansys_sphinx_theme_autoapi': {
        'project': project,
        'own_page_level': 'function',
        'class_content': 'both',  # documentation in https://sphinxdocs.ansys.com/version/stable/user-guide/autoapi.html
        'member_order': 'alphabetical',
        'ignore': ['*/src/ansys/scade/wux/impl/*', '*/src/ansys/scade/wux/test/*'],
    },
}

# Configuration for Sphinx autoapi
# TODO autoapi_render_in_single_page = ["class", "enum", "exception", "function"]

# Sphinx extensions
extensions = [
    'sphinx.ext.intersphinx',
    'sphinx_copybutton',
    'sphinx_design',
    'ansys_sphinx_theme.extension.autoapi',
    'sphinx.ext.autosectionlabel',
    'breathe',
]

# Make sure the target is unique
autosectionlabel_prefix_document = True

# # ansys.scade.wux.info not found when building the documentation
suppress_warnings = ['autoapi.python_import_resolution', 'autosectionlabel.*']

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3.11', None),
    # kept here as an example
    # "scipy": ("https://docs.scipy.org/doc/scipy/reference", None),
    # "numpy": ("https://numpy.org/devdocs", None),
    # "matplotlib": ("https://matplotlib.org/stable", None),
    # "pandas": ("https://pandas.pydata.org/pandas-docs/stable", None),
    # "pyvista": ("https://docs.pyvista.org/", None),
    # "grpc": ("https://grpc.github.io/grpc/python/", None),
}

# numpydoc configuration
numpydoc_show_class_members = False
numpydoc_xref_param_type = True

# Consider enabling numpydoc validation. See:
# https://numpydoc.readthedocs.io/en/latest/validation.html#
numpydoc_validate = True
numpydoc_validation_checks = {
    'GL06',  # Found unknown section
    'GL07',  # Sections are in the wrong order.
    # Disabled the docstring validation as most of the methods doesn't have the docstring
    # TODO: Add docstring and enable GL08 validation
    # "GL08",  # The object does not have a docstring
    'GL09',  # Deprecation warning should precede extended summary
    'GL10',  # reST directives {directives} must be followed by two colons
    'SS01',  # No summary found
    'SS02',  # Summary does not start with a capital letter
    'SS03',  # Summary does not end with a period
    'SS04',  # Summary contains heading whitespaces
    # "SS05", # Summary must start with infinitive verb, not third person
    'RT02',  # The first line of the Returns section should contain only the
    # type, unless multiple values are being returned"
}

# Favicon
html_favicon = ansys_favicon

# static path
html_static_path = ['_static']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# TODO: remove ignore links after public release
linkcheck_ignore = [
    'https://github.com/ansys/scade-wux',
    'https://github.com/ansys/scade-wux/actions/workflows/ci_cd.yml',
    'https://pypi.org/project/ansys-scade-wux',
    # The link below takes a long time to check
    'https://www.ansys.com/products/embedded-software/ansys-scade-suite',
    'https://www.ansys.com/*',
]

if switcher_version != 'dev':
    linkcheck_ignore.append(f'https://github.com/ansys/scade-wux/releases/tag/v{__version__}')

# -- Import the C++ docs -----------------------------------------------------

# Define directory paths
SOURCE_DIR = Path(__file__).parent
ROOT_DIR = SOURCE_DIR.parent.parent
DOXYGEN_DIR = SOURCE_DIR / '_doxygen'

# Ensure the output directory exists
DOXYGEN_DIR.mkdir(exist_ok=True)

# path of doxygen configuration files are relative to the current directory
# -> copy the configuration file from a template, patched with an
#    absolute directory, so that the command is independent from the
#    current directory
# Read and patch the Doxygen configuration template
template_path = SOURCE_DIR / '_templates' / 'includes.dox'
output_path = DOXYGEN_DIR / 'includes.dox'

text = template_path.read_text(encoding='utf-8').replace('{{repository}}', str(ROOT_DIR))
output_path.write_text(text, encoding='utf-8')

# Run Doxygen with the patched configuration file
subprocess.call(['doxygen', str(output_path)])

breathe_projects = {
    'interfaces': f'{DOXYGEN_DIR}/xml/',
}
breathe_default_project = 'interfaces'

breathe_projects_source = {
    'interfaces': (
        f'{ROOT_DIR}/src/ansys/scade/wux/include',
        [
            'WuxA661Ext.h',
            'WuxCtxExt.h',
            'WuxDllExt.h',
            'WuxSdyExt.h',
            'WuxSdyProxy.h',
            'WuxSimuExt.h',
        ],
    ),
}
breathe_show_include = False
breathe_separate_member_pages = True

breathe_doxygen_config_options = {
    'PREDEFINED': '__cplusplus NO_DOXYGEN',
}
