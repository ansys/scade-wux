# Copyright (C) 2020 - 2024 ANSYS, Inc. and/or its affiliates.
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

"""Wraps scade.code.suite.sctoc to allow unit testing."""

from typing import List, Optional, Tuple

import scade.code.suite.sctoc as _sctoc
from scade.model.project.stdproject import Configuration, Project


# interface
def get_operator_sample_time() -> Tuple[float, float, bool]:
    return _sctoc.get_operator_sample_time()


def get_list_of_project_files(*file_exts: str) -> List[str]:
    return _sctoc.get_list_of_project_files(*file_exts)


def get_list_of_project_files2(
    file_exts: Optional[List[str]] = None,
    project: Optional[Project] = None,
    configuration: Optional[Configuration] = None,
) -> List[str]:
    return _sctoc.get_list_of_project_files2(file_exts, project, configuration)


def get_list_of_external_files(*kinds: str) -> List[str]:
    return _sctoc.get_list_of_project_files(*kinds)


# adding make directives
def add_c_files(c_files: List[str], relative: bool, service: str):
    _sctoc.add_c_files(c_files, relative, service)


def add_ada_files(ada_files: List[str], relative: bool, service: str):
    _sctoc.add_ada_files(ada_files, relative, service)


def add_obj_files(obj_files: List[str], relative: bool):
    _sctoc.add_obj_files(obj_files, relative)


def add_include_files(directories: List[str], relative: bool):
    _sctoc.add_include_files(directories, relative)


def add_dynamic_library_rule(
    basename: str,
    c_files: List[str],
    o_files: List[str],
    def_files: list[str],
    dependencies: List[str],
    main: bool,
    cpu_type: str = '',
    language: str = '',
):
    _sctoc.add_dynamic_library_rule(
        basename, c_files, o_files, def_files, dependencies, main, cpu_type, language
    )


def add_static_library_rule(
    basename: str, c_files: List[str], o_files: List[str], main: bool, cpu_type: str, language: str
):
    _sctoc.add_static_library_rule(basename, c_files, o_files, main, cpu_type, language)


def add_executable_rule(
    basename: str,
    c_files: List[str],
    o_files: List[str],
    dependencies: List[str],
    main: bool,
    cpu_type: str = '',
    language: str = '',
):
    _sctoc.add_executable_rule(basename, c_files, o_files, dependencies, main, cpu_type, language)


def add_custom_rule(
    basename: str,
    dependencies: List[str],
    commands: List[str],
    main: bool,
    cpu_type: str = '',
    language: str = '',
):
    _sctoc.add_custom_rule(basename, dependencies, commands, main, cpu_type, language)


def add_variable(name: str, value: str):
    _sctoc.add_variable(name, value)


def add_path_variable(name: str, value: str, relative: bool):
    _sctoc.add_path_variable(name, value, relative)


def set_compiler_kind(kind: str):
    _sctoc.set_compiler_kind(kind)


def add_preprocessor_definitions(*definitions: str):
    _sctoc.add_preprocessor_definitions(*definitions)


def get_compiler_object_directory() -> str:
    return _sctoc.get_compiler_object_directory()


# sending feedback to SCADE Suite user interface
def add_error(category: str, code: str, messages: List[Tuple[str, str]]):
    _sctoc.add_error(category, code, messages)


def add_warning(category: str, code: str, messages: List[Tuple[str, str]]):
    _sctoc.add_warning(category, code, messages)


def add_information(category: str, code: str, messages: List[Tuple[str, str]]):
    _sctoc.add_information(category, code, messages)


def add_generated_files(service: str, files: List[str]):
    _sctoc.add_generated_files(service, files)


# misc. (undocumented)
def is_state_up_to_date(state_ext: str) -> bool:
    return _sctoc.is_state_up_to_date(state_ext)


def save_state(state_files: List[str], state_ext: str):
    _sctoc.save_state(state_files, state_ext)
