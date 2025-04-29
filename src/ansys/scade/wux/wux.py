# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Provides a collection of functions for developing wrappers."""

from io import TextIOBase
import os
from pathlib import Path
import re
from typing import List, Optional, Set

from scade.code.suite.mapping.c import MappingFile
import scade.code.suite.sctoc as sctoc
from scade.code.suite.wrapgen.c import InterfacePrinter
from scade.code.suite.wrapgen.model import MappingHelpers
from scade.model.project.stdproject import Configuration, Project
from scade.model.suite import Session, get_roots as _get_sessions
from scade.model.suite.displaycoupling import (
    SdyApplication,
    Specification,
    get_roots as _get_sdy_applications,
)

# globals
mf: Optional[MappingFile] = None
"""
KCG Mapping File data.

This attribute is initialized by the ``WuxContext`` generation service.
"""
mh: Optional[MappingHelpers] = None
"""
WrapGen API MappingHelpers instance for the current project.

This attribute is initialized by the ``WuxContext`` generation service.
"""
ips: List[InterfacePrinter] = []
"""
List of WrapGen API InterfacePrinter instances for the root operators.

This attribute is initialized by the ``WuxContext`` generation service.
"""


# generated C files, for makefile
_sources: Set[str] = set()
# build
_libraries: Set[str] = set()
_includes: Set[str] = set()
_definitions: Set[str] = set()
# roots for APIs
_sessions: List[Session] = []
_sdy_applications: List[SdyApplication] = []
# cache
_specifications: List[Specification] = []


def reset():
    """
    Reset the global module's global variables.

    Used for unit testing.
    """
    global \
        _sources, \
        _libraries, \
        _includes, \
        _definitions, \
        _sessions, \
        _sdy_applications, \
        _specifications

    # generated C files, for makefile
    _sources = set()
    # build
    _libraries = set()
    _includes = set()
    _definitions = set()
    # APIs
    _sessions = []
    _sdy_applications = []
    # cache
    _specifications = []


def add_sources(paths: List[Path]):
    """
    Request the Code Generator to add sources files to the Makefile for C build.

    The source files are associated to the virtual service ``WUX``:
    Use the dependency ``WUX`` to declare a new target containing the sources
    from the generation services, either generated ones or runtime files.

    This function may be called by different generation services.
    It caches the added sources so that they are not added twice to the makefile.

    Refer to ``add_c_files`` under *Adding Make Directives* in section 3
    of the *SCADE Python API Guide* in the SCADE Suite documentation.

    Parameters
    ----------
    paths : List[Path]
        Paths of the C/C++ sources files to be added to the makefile.
    """
    global _sources

    # prevent adding the source file twice to sctoc
    set_paths = {_.as_posix() for _ in paths}
    sctoc.add_c_files(list(set_paths - _sources), False, 'WUX')
    _sources |= set_paths


def add_includes(paths: List[Path]):
    """
    Request the Code Generator to add include directories directives to the Makefile.

    This function may be called by different generation services.
    It caches the added include directories so that they are not added twice to the makefile.

    Refer to ``add_include_files`` under *Adding Make Directives* in section 3
    of the *SCADE Python API Guide* in the SCADE Suite documentation.

    Parameters
    ----------
    paths : List[Path]
        Paths of the include directories to be added to the makefile.
    """
    global _includes

    # prevent adding the directory file twice to sctoc
    set_paths = {_.as_posix() for _ in paths}
    sctoc.add_include_files(list(set_paths - _includes), False)
    _includes |= set_paths


def add_libraries(paths: List[Path]):
    """
    Request the Code Generator to add object or library files to the Makefile.

    This function may be called by different generation services.
    It caches the added files so that they are not added twice to the makefile.

    Refer to ``add_obj_files`` under *Adding Make Directives* in section 3
    of the *SCADE Python API Guide* in the SCADE Suite documentation.

    Parameters
    ----------
    paths : List[Path]
        Paths of the files to be added to the makefile.
    """
    global _libraries

    set_paths = {_.as_posix() for _ in paths}
    sctoc.add_object_files(list(set_paths - _libraries), False)
    _libraries |= set_paths


def add_definitions(*definitions: str):
    """
    Request the Code Generator to add preprocessor definitions to the Makefile.

    This function may be called by different generation services.
    It caches the added definitions so that they are not added twice to the makefile.

    Refer to ``add_preprocessor_definitions`` under *Adding Make Directives*
    in section 3 of the *SCADE Python API Guide* in the SCADE Suite documentation.

    Parameters
    ----------
    *definitions : str
        Preprocessor definitions to be added to the makefile.
    """
    # prevent adding the preprocessor definition twice to sctoc
    global _definitions

    set_definitions = {_ for _ in definitions}
    sctoc.add_preprocessor_definitions(*(set_definitions - _definitions))
    _definitions |= set_definitions


def add_cpp_options(project: Project, configuration: Configuration):
    """
    Add the required compiler/linker options for C++ code.

    * This is required for GNU C: -static -lstdc++
    * There is no API in scade.code.suite.* to achieve this. The workaround
      consists in adding the option to the project for the given configuration.

    .. Note::

      * The option is set only if the current compiler is GNU C.
      * The project is modified but it is not expected to be saved in this context.
        Should it be saved, this is still fine since the option is mandatory.

    Parameters
    ----------
    project : Project
        Input project.
    configuration : Configuration
        Input configuration.
    """
    # the default value is 'GNU C' when the property is not set
    compiler = project.get_scalar_tool_prop_def('SIMULATOR', 'COMPILER', 'GNU C', configuration)
    if compiler != 'GNU C':
        return
    # add the platform: x64 is the only one supported
    compiler += 'win64'
    linker_options = project.get_scalar_tool_prop_def(
        compiler, 'ADD_LINK_OPTIONS', '', configuration
    )
    new_linker_options = linker_options
    for option in ['-static', '-lstdc++']:
        if option not in linker_options:
            new_linker_options += ' ' + option
    if new_linker_options != linker_options:
        project.set_scalar_tool_prop_def(
            compiler, 'ADD_LINK_OPTIONS', new_linker_options, '', configuration
        )


def writeln(f: TextIOBase, num_tabs: int = 0, text: str = ''):
    """
    Write a text with a level of indentation.

    The function writes four (4) spaces per level of indentation.

    Parameters
    ----------
    f : TextIOBase
        Output file to write to.

    num_tabs : int
        Level of indentation.

    text : str
        Input text.
    """
    f.write('    ' * num_tabs)
    f.write(text)
    f.write('\n')


def write_indent(f: TextIOBase, tab: str, text: str):
    """
    Write a multi-lined text with an indentation.

    The function splits the test into lines and writes each line
    with the prefix ``tab``.

    Parameters
    ----------
    f : TextIOBase
        Output file to write to.

    tab : str
        Prefix.

    text : str
        Input text.
    """
    if text != '':
        f.write(tab)
        f.write(('\n' + tab).join(text.strip('\n').split('\n')))
        f.write('\n')


def gen_start_protect(f: TextIOBase, name: str):
    """
    Write the beginning of a protection macro for a ``C`` header file.

    * The dots (``.``) present in name are replaced by underscores (``_``).
    * The name of the macro is uppercase.

    The function writes the following snippet:

    .. code-block:: c

       #ifndef _NAME_
       #define _NAME_

    Parameters
    ----------
    f : TextIOBase
        Output file to write to.

    name : str
        Name of the preprocessor macro.
    """
    macro = '_' + name.replace('.', '_').upper() + '_'
    writeln(f, 0, '#ifndef {0}\n#define {0}'.format(macro))
    writeln(f)


def gen_end_protect(f: TextIOBase, name: str):
    """
    Write the end of a protection macro for a ``C`` header file.

    * The dots (``.``) present in name are replaced by underscores (``_``).
    * The name of the macro is uppercase.

    The function writes the following snippet:

    .. code-block:: c

       #endif /* _NAME_ */

    Parameters
    ----------
    f : TextIOBase
        Output file to write to.

    name : str
        Name of the preprocessor macro.
    """
    macro = '_' + name.replace('.', '_').upper() + '_'
    writeln(f, 0, '#endif /* {0} */'.format(macro))
    writeln(f)


def gen_header(f: TextIOBase, banner: str, start_comment: str = '/* ', end_comment: str = ' */'):
    r"""
    Write a *generated by* comment.

    Parameters
    ----------
    f : TextIOBase
        Output file to write to.

    banner : str
        Text to write.

    start_comment : str
        Start comment, default "/\* ".

    end_comment : str
        End comment, default " \*/".
    """
    writeln(f, 0, '{1}generated by {0}{2}'.format(banner, start_comment, end_comment))
    writeln(f)


def gen_footer(f: TextIOBase, start_comment: str = '/* ', end_comment: str = ' */'):
    r"""
    Write an *end of file* comment.

    Parameters
    ----------
    f : TextIOBase
        Output file to write to.

    start_comment : str
        Start comment, default "/\* ".

    end_comment : str
        End comment, default " \*/".
    """
    writeln(f, 0, '{0}end of file{1}'.format(start_comment, end_comment))


def gen_includes(f: TextIOBase, files: List[str]):
    """
    Write C include directives for a list of files.

    The function prefixes the include directives with ``/* includes */``.

    Parameters
    ----------
    f : TextIOBase
        Output file to write to.

    files : List[str]
        List of files to be included.
    """
    writeln(f, 0, '/* includes */')
    for file in files:
        writeln(f, 0, '#include "%s"' % file)
    writeln(f)


def get_sessions() -> List[Session]:
    """
    Return the loaded SCADE models.

    The nominal use case consists in calling SCADE Suite API's ``get_roots()``,
    unless the list of sessions has already been initialized,
    for unit testing for example.

    Returns
    -------
    List[Session]
    """
    global _sessions

    if not _sessions:
        _sessions = _get_sessions()
    return _sessions


def set_sessions(sessions: List[Session]):
    """
    Set the list of loaded SCADE models.

    This function is present only for unit testing, where SCADE Suite API's ``get_roots()``
    cannot be used.

    Parameters
    ----------
    sessions : List[Session]
        List of loaded SCADE Suite models.
    """
    global _sessions

    _sessions = sessions


def get_sdy_applications() -> List[SdyApplication]:
    """
    Return the loaded SCADE models.

    The nominal use case consists in calling SCADE Display Coupling API's ``get_roots()``,
    unless the list of applications has already been initialized,
    for unit testing for example.

    Returns
    -------
    List[Session]
    """
    global _sdy_applications

    if not _sdy_applications:
        _sdy_applications = _get_sdy_applications()
    return _sdy_applications


def set_sdy_applications(sdy_applications: List[SdyApplication]):
    """
    Set the list of loaded SCADE Display Coupling applications.

    This function is present only for unit testing, where SCADE Display Coupling API's
    ``get_roots()`` cannot be used.

    Parameters
    ----------
    sdy_applications : List[SdyApplication]
        List of loaded SCADE Display Coupling models.
    """
    global _sdy_applications

    _sdy_applications = sdy_applications


def get_specifications(project: Project, configuration: Configuration) -> List[Specification]:
    """
    Return the list of graphical panel specifications selected for the input configuration.

    This function adds a new ``prefix`` attribute to the specifications.

    Parameters
    ----------
    project : Project
        Input project.
    configuration : Configuration
        Input configuration.

    Returns
    -------
    List[Specification]
    """
    global _specifications

    sdy_applications = get_sdy_applications()
    if not _specifications and sdy_applications:
        # must be only one application
        sdy_application = sdy_applications[0]
        if not sdy_application.mapping_file:
            return _specifications
        sdy_map_file_dir = os.path.dirname(sdy_application.mapping_file.pathname)
        for panel_params in project.get_tool_prop_def(
            'GENERATOR', 'DISPLAY_ENABLED_PANELS', [], configuration
        ):
            params = panel_params.split(',')
            if len(params) >= 2 and params[1] != 'None':
                for spec in sdy_application.specifications:
                    if (
                        os.path.abspath(spec.pathname)
                        == os.path.abspath(os.path.join(sdy_map_file_dir, params[0]))
                    ) and (spec.sdy_project.is_display() or spec.sdy_project.is_rapid_proto()):
                        _specifications.append(spec)
                        # set spec.conf and spec.basename
                        spec.conf = params[1]
                        spec.basename = os.path.splitext(os.path.basename(spec.pathname))[0]
        # sort specifications by basename
        _specifications = sorted(_specifications, key=lambda x: x.basename)
        # compute specifications prefix
        for id_spec_file, spec in enumerate(_specifications, start=1):
            # add an attribute `prefix` to Specification
            spec.prefix = 'SDY{}_{}'.format(
                id_spec_file, re.sub(r'[^A-Za-z0-9_]', '_', spec.basename)
            )

    return _specifications
