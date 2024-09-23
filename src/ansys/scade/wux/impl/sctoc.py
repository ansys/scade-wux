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

try:
    import scade.code.suite.sctoc as _sctoc

    _stub = False
except ModuleNotFoundError:
    # avoid too much code in an exception handler
    _stub = True
from scade.model.project.stdproject import Configuration, Project

if _stub:

    class _SCToCStub:
        """Stubs sctoc and stores all the data declared through its calls."""

        def __init__(self, sample_time: Tuple[float, float, bool] = (0.02, 0.0, True)) -> None:
            # getting information from input project and model
            self.sample_time = sample_time

            # sending feedback to SCADE Suite user interface
            # dict str -> list [str, List[Tuple[str, str]]]
            self.errors = {}
            # dict str -> list [str, List[Tuple[str, str]]]
            self.warnings = {}
            # dict str -> list [str, List[Tuple[str, str]]]
            self.infos = {}
            # dict str -> list[str]

            self.generated_files = {}
            # adding make directives
            # dictionary str -> list[tuple[str, bool]]
            self.c_files = {}
            # dictionary str -> list[tuple[str, bool]]
            self.ada_files = {}
            # list[str, bool]
            self.obj_files = []
            # list[str, bool]
            self.includes = []
            # list[tuple(...)]
            self.dynamic_library_rules = []
            # list[tuple(...)]
            self.static_library_rules = []
            # list[tuple(...)]
            self.static_executable_rules = []
            # list[tuple(...)]
            self.custom_rules = []
            # list[tuple[str, str]]
            self.variables = []
            # list[tuple[str, str, bool]]
            self.path_variables = []
            # str
            self.compiler_kind = ''
            # list[str]
            self.preprocessor_definitions = []

        # getting information from input project and model
        # methods to be overridden in a sub-class for given unit tests
        def get_operator_sample_time(self) -> Tuple[float, float, bool]:
            return self.sample_time

        def get_list_of_project_files(self, *file_exts: str) -> List[str]:
            # do some usage of the parameters to avoid linter warnings
            for ext in list(*file_exts):
                assert isinstance(ext, str)
            return []

        def get_list_of_project_files2(
            self,
            file_exts: Optional[List[str]] = None,
            project: Optional[Project] = None,
            configuration: Optional[Configuration] = None,
        ) -> List[str]:
            if not file_exts:
                file_exts = []
            # do some usage of the parameters to avoid linter warnings
            assert not project or isinstance(project, Project)
            assert not configuration or isinstance(configuration, Configuration)
            return []

        def get_list_of_external_files(self, *kinds: str) -> List[str]:
            # do some usage of the parameters to avoid linter warnings
            for kind in list(*kinds):
                assert isinstance(kind, str)
            return []

        # adding make directives
        def add_c_files(self, c_files: List[str], relative: bool, service: str):
            self.c_files.setdefault(service, []).extend([(_, relative) for _ in c_files])

        def add_ada_files(self, ada_files: List[str], relative: bool, service: str):
            self.ada_files.setdefault(service, []).extend([(_, relative) for _ in ada_files])

        def add_obj_files(self, obj_files: List[str], relative: bool):
            self.obj_files.extend([(_, relative) for _ in obj_files])

        def add_include_files(self, directories: List[str], relative: bool):
            self.includes.extend([(_, relative) for _ in directories])

        def add_dynamic_library_rule(
            self,
            basename: str,
            c_files: List[str],
            o_files: List[str],
            def_files: list[str],
            dependencies: List[str],
            main: bool,
            cpu_type: str,
            language: str,
        ):
            self.dynamic_library_rules.append(
                (basename, c_files, o_files, def_files, dependencies, main, cpu_type, language),
            )

        def add_static_library_rule(
            self,
            basename: str,
            c_files: List[str],
            o_files: List[str],
            main: bool,
            cpu_type: str,
            language: str,
        ):
            self.static_library_rules.append(
                (basename, c_files, o_files, main, cpu_type, language),
            )

        def add_executable_rule(
            self,
            basename: str,
            c_files: List[str],
            o_files: List[str],
            dependencies: List[str],
            main: bool,
            cpu_type: str,
            language: str,
        ):
            self.static_executable_rules.append(
                (basename, c_files, o_files, dependencies, main, cpu_type, language),
            )
            pass

        def add_custom_rule(
            self,
            basename: str,
            dependencies: List[str],
            commands: List[str],
            main: bool,
            cpu_type: str,
            language: str,
        ):
            self.custom_rules.append(
                (basename, dependencies, commands, main, cpu_type, language),
            )
            pass

        def add_variable(self, name: str, value: str):
            self.variables.append((name, value))

        def add_path_variable(self, name: str, value: str, relative: bool):
            self.path_variables.append((name, value, relative))

        def set_compiler_kind(self, kind: str):
            self.compiler_kind = kind

        def add_preprocessor_definitions(self, *definitions: str):
            self.preprocessor_definitions.extend(*definitions)

        def get_compiler_object_directory(self) -> str:
            return ''

        # sending feedback to SCADE Suite user interface
        def add_error(self, category: str, code: str, messages: List[Tuple[str, str]]):
            self.errors.setdefault(category, []).append((code, messages))

        def add_warning(self, category: str, code: str, messages: List[Tuple[str, str]]):
            self.warnings.setdefault(category, []).append((code, messages))

        def add_information(self, category: str, code: str, messages: List[Tuple[str, str]]):
            self.infos.setdefault(category, []).append((code, messages))

        def add_generated_files(self, service: str, files: List[str]):
            self.infos.setdefault(service, []).extend(files)

        # misc. (undocumented)
        def is_state_up_to_date(self, state_ext: str) -> bool:
            # do some usage of the parameters to avoid linter warnings
            assert isinstance(state_ext, str)
            # consider a file is always obsolete
            return False

        def save_state(self, state_files: List[str], state_ext: str):
            for file in list(*state_files):
                assert isinstance(file, str)
            assert isinstance(state_ext, str)

    # sctoc is an instance, not a module, so that unit tests
    # can access its state, or replace it
    sctoc = _SCToCStub()


# interface
def get_operator_sample_time() -> Tuple[float, float, bool]:
    return sctoc.get_operator_sample_time() if _stub else _sctoc.get_operator_sample_time()


def get_list_of_project_files(*file_exts: str) -> List[str]:
    return (
        sctoc.get_list_of_project_files(*file_exts)
        if _stub
        else _sctoc.get_list_of_project_files(*file_exts)
    )


def get_list_of_project_files2(
    file_exts: Optional[List[str]] = None,
    project: Optional[Project] = None,
    configuration: Optional[Configuration] = None,
) -> List[str]:
    return (
        sctoc.get_list_of_project_files2(file_exts, project, configuration)
        if _stub
        else _sctoc.get_list_of_project_files2(file_exts, project, configuration)
    )


def get_list_of_external_files(*kinds: str) -> List[str]:
    return (
        sctoc.get_list_of_project_files(*kinds)
        if _stub
        else _sctoc.get_list_of_project_files(*kinds)
    )


# adding make directives
def add_c_files(c_files: List[str], relative: bool, service: str):
    if _stub:
        sctoc.add_c_files(c_files, relative, service)
    else:
        _sctoc.add_c_files(c_files, relative, service)


def add_ada_files(ada_files: List[str], relative: bool, service: str):
    if _stub:
        sctoc.add_ada_files(ada_files, relative, service)
    else:
        _sctoc.add_ada_files(ada_files, relative, service)


def add_obj_files(obj_files: List[str], relative: bool):
    if _stub:
        sctoc.add_obj_files(obj_files, relative)
    else:
        _sctoc.add_obj_files(obj_files, relative)


def add_include_files(directories: List[str], relative: bool):
    if _stub:
        sctoc.add_include_files(directories, relative)
    else:
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
    if _stub:
        sctoc.add_dynamic_library_rule(
            basename, c_files, o_files, def_files, dependencies, main, cpu_type, language
        )
    else:
        _sctoc.add_dynamic_library_rule(
            basename, c_files, o_files, def_files, dependencies, main, cpu_type, language
        )


def add_static_library_rule(
    basename: str, c_files: List[str], o_files: List[str], main: bool, cpu_type: str, language: str
):
    if _stub:
        sctoc.add_static_library_rule(basename, c_files, o_files, main, cpu_type, language)
    else:
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
    if _stub:
        sctoc.add_executable_rule(
            basename, c_files, o_files, dependencies, main, cpu_type, language
        )
    else:
        _sctoc.add_executable_rule(
            basename, c_files, o_files, dependencies, main, cpu_type, language
        )


def add_custom_rule(
    basename: str,
    dependencies: List[str],
    commands: List[str],
    main: bool,
    cpu_type: str = '',
    language: str = '',
):
    if _stub:
        sctoc.add_custom_rule(basename, dependencies, commands, main, cpu_type, language)
    else:
        _sctoc.add_custom_rule(basename, dependencies, commands, main, cpu_type, language)


def add_variable(name: str, value: str):
    if _stub:
        sctoc.add_variable(name, value)
    else:
        _sctoc.add_variable(name, value)


def add_path_variable(name: str, value: str, relative: bool):
    if _stub:
        sctoc.add_path_variable(name, value, relative)
    else:
        _sctoc.add_path_variable(name, value, relative)


def set_compiler_kind(kind: str):
    if _stub:
        sctoc.set_compiler_kind(kind)
    else:
        _sctoc.set_compiler_kind(kind)


def add_preprocessor_definitions(*definitions: str):
    if _stub:
        sctoc.add_preprocessor_definitions(*definitions)
    else:
        _sctoc.add_preprocessor_definitions(*definitions)


def get_compiler_object_directory() -> str:
    return (
        sctoc.get_compiler_object_directory() if _stub else _sctoc.get_compiler_object_directory()
    )


# sending feedback to SCADE Suite user interface
def add_error(category: str, code: str, messages: List[Tuple[str, str]]):
    if _stub:
        sctoc.add_error(category, code, messages)
    else:
        _sctoc.add_error(category, code, messages)


def add_warning(category: str, code: str, messages: List[Tuple[str, str]]):
    if _stub:
        sctoc.add_warning(category, code, messages)
    else:
        _sctoc.add_warning(category, code, messages)


def add_information(category: str, code: str, messages: List[Tuple[str, str]]):
    if _stub:
        sctoc.add_information(category, code, messages)
    else:
        _sctoc.add_information(category, code, messages)


def add_generated_files(service: str, files: List[str]):
    if _stub:
        sctoc.add_generated_files(service, files)
    else:
        _sctoc.add_generated_files(service, files)


# misc. (undocumented)
def is_state_up_to_date(state_ext: str) -> bool:
    return sctoc.is_state_up_to_date(state_ext) if _stub else _sctoc.is_state_up_to_date(state_ext)


def save_state(state_files: List[str], state_ext: str):
    if _stub:
        sctoc.save_state(state_files, state_ext)
    else:
        _sctoc.save_state(state_files, state_ext)
