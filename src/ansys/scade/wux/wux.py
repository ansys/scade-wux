# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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
from pathlib import Path
from typing import List, Optional, Set

from scade.code.suite.mapping.c import MappingFile
import scade.code.suite.sctoc as sctoc
from scade.code.suite.wrapgen.c import InterfacePrinter
from scade.code.suite.wrapgen.model import MappingHelpers

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


def add_sources(paths: List[Path]):
    """
    Request the Code Generator to add sources files to the Makefile for C build.

    The source files are associated to the virtual service ``WUX``:
    Use the dependency ``WUX`` to declare a new target containing the sources
    from the generation services, either generated ones or runtime files.

    This function may be called by different generation services.
    It caches the added sources so that they are not added twice to the makefile.

    Refer to ``add_c_files`` in the User Documentation, section *Adding Make Directives*.

    Parameters
    ----------
    paths : List[Path]
        Paths of the C/C++ sources files to be added to the makefile.
    """
    global _sources

    # prevent adding the source file twice to sctoc
    paths = {_.as_posix() for _ in paths}
    sctoc.add_c_files(list(paths - _sources), False, 'WUX')
    _sources |= paths


def add_includes(paths: List[Path]):
    """
    Request the Code Generator to add include directories directives to the Makefile.

    This function may be called by different generation services.
    It caches the added include directories so that they are not added twice to the makefile.

    Refer to ``add_include_files`` in the User Documentation, section *Adding Make Directives*.

    Parameters
    ----------
    paths : List[Path]
        Paths of the include directories to be added to the makefile.
    """
    global _includes

    # prevent adding the directory file twice to sctoc
    paths = {_.as_posix() for _ in paths}
    sctoc.add_include_files(list(paths - _includes), False)
    _includes |= paths


def add_libraries(paths: List[Path]):
    """
    Request the Code Generator to add object or library files to the Makefile.

    This function may be called by different generation services.
    It caches the added files so that they are not added twice to the makefile.

    Refer to ``add_obj_files`` in the User Documentation, section *Adding Make Directives*.

    Parameters
    ----------
    paths : List[Path]
        Paths of the files to be added to the makefile.
    """
    global _libraries

    paths = {_.as_posix() for _ in paths}
    sctoc.add_obj_files(list(paths - _libraries), False)
    _libraries |= paths


# prevent adding the preprocessor definition twice to sctoc
def add_definitions(*definitions: str):
    """
    Request the Code Generator to add preprocessor definitions to the Makefile.

    This function may be called by different generation services.
    It caches the added definitions so that they are not added twice to the makefile.

    Refer to ``add_preprocessor_definitions`` in the User Documentation,
    section *Adding Make Directives*.

    Parameters
    ----------
    *definitions : str
        Preprocessor definitions to be added to the makefile.
    """
    # prevent adding the preprocessor definition twice to sctoc
    global _definitions

    definitions = {_ for _ in definitions}
    sctoc.add_preprocessor_definitions(*(definitions - _definitions))
    _definitions |= definitions


def writeln(f: TextIOBase, num_tabs: int = 0, text: str = ''):
    """
    Write a text with a level of indentation.

    The function writes four (4) spaces per level of indentation.

    Parameters
    ----------
    f: TextIOBase
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
    f: TextIOBase
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
    f: TextIOBase
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
    f: TextIOBase
        Output file to write to.

    name : str
        Name of the preprocessor macro.
    """
    macro = '_' + name.replace('.', '_').upper() + '_'
    writeln(f, 0, '#endif /* {0} */'.format(macro))
    writeln(f)


def gen_header(f: TextIOBase, banner: str, start_comment: str = '/* ', end_comment: str = ' */'):
    r"""
    Write a comment line.

    This is usually used for writing a banner.

    Parameters
    ----------
    f: TextIOBase
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
    f: TextIOBase
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
    f: TextIOBase
        Output file to write to.

    files : List[str]
        List of files to be included.
    """
    writeln(f, 0, '/* includes */')
    for file in files:
        writeln(f, 0, '#include "%s"' % file)
    writeln(f)
