# Copyright (C) 2020 - 2025 ANSYS, Inc. and/or its affiliates.
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

"""
Wraps ``scade.code.suite.sctoc`` to allow unit testing.

Redirects the entry points of ``scade.code.suite.sctoc`` to this module.
"""

from typing import List, Tuple

import scade.code.suite.sctoc as sctoc


class SCToCStub:
    """Stubs ``sctoc`` and stores all the data declared through its calls."""

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
        """
        Return the period, offset, periodic properties for the model.

        These properties are defined in Periodicity frame of Code Integration tab.
        """
        return self.sample_time

    def get_list_of_project_files(self, *args, **kwargs) -> List[str]:
        """
        Return a list of file paths referenced by the current project and its libraries.

        This list filtered according to provided file extensions.
        """
        # two different interfaces in the documentation
        return []

    def get_list_of_external_files(self, *kinds: str) -> List[str]:
        """
        Return a list of external files referenced by the current project and its libraries.

        This list is filtered according to file kinds: ``CS``, ``AdaS``, ``Obj``, ``Macro``,
        or ``Type``.
        """
        # do some usage of the parameters to avoid linter warnings
        for kind in list(*kinds):
            assert isinstance(kind, str)
        return []

    # adding make directives
    def add_c_files(self, c_files: List[str], relative: bool, service: str):
        """Request ``scade -code`` to add sources files to the Makefile for C build."""
        self.c_files.setdefault(service, []).extend([(_, relative) for _ in c_files])

    def add_ada_files(self, ada_files: List[str], relative: bool, service: str):
        """Request ``scade -code`` to add sources files to the Makefile for Ada build."""
        self.ada_files.setdefault(service, []).extend([(_, relative) for _ in ada_files])

    def add_object_files(self, obj_files: List[str], relative: bool):
        """Request ``scade -code`` to add object files to the Makefile."""
        self.obj_files.extend([(_, relative) for _ in obj_files])

    def add_include_files(self, directories: List[str], relative: bool):
        """Request ``scade -code`` to add include directories directives to the Makefile."""
        self.includes.extend([(_, relative) for _ in directories])

    def add_dynamic_library_rule(
        self,
        basename: str,
        c_files: List[str],
        o_files: List[str],
        def_files: List[str],
        dependencies: List[str],
        main: bool,
        cpu_type: str,
        language: str,
    ):
        """Request ``scade -code`` to add a dynamic library (.dll) build rule to the Makefile."""
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
        """Request ``scade -code`` to add a static library (.lib) build rule to the Makefile."""
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
        """Request ``scade -code`` to add an executable (.exe) build rule to the Makefile."""
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
        """Request ``scade -code`` to add a custom build rule to the Makefile."""
        self.custom_rules.append(
            (basename, dependencies, commands, main, cpu_type, language),
        )
        pass

    def add_variable(self, name: str, value: str):
        """Request ``scade -code`` to add line ``<variable>=<value>`` to the Makefile."""
        self.variables.append((name, value))

    def add_path_variable(self, name: str, value: str, relative: bool):
        """Request ``scade -code`` to add line ``<variable>=<path>`` to the Makefile."""
        self.path_variables.append((name, value, relative))

    def set_compiler_kind(self, kind: str):
        """Specify ``scade -code`` the kind of compiler expected to be used."""
        self.compiler_kind = kind

    def add_preprocessor_definitions(self, *definitions: str):
        """Request ``scade -code`` to add preprocessor definitions to the Makefile."""
        self.preprocessor_definitions.extend(definitions)

    def get_compiler_object_directory(self) -> str:
        """Return the object directory for the selected compiler and CPU Type."""
        return ''

    # sending feedback to SCADE Suite user interface
    def add_error(self, category: str, code: str, messages: List[Tuple[str, str]]):
        """Display error messages."""
        self.errors.setdefault(category, []).append((code, messages))

    def add_warning(self, category: str, code: str, messages: List[Tuple[str, str]]):
        """Display warning messages."""
        self.warnings.setdefault(category, []).append((code, messages))

    def add_information(self, category: str, code: str, messages: List[Tuple[str, str]]):
        """Display information messages."""
        self.infos.setdefault(category, []).append((code, messages))

    def add_generated_files(self, service: str, files: List[str]):
        """Display the list of files generated by the extension."""
        self.generated_files.setdefault(service, []).extend(files)

    # misc. (undocumented)
    def is_state_up_to_date(self, state_ext: str) -> bool:
        """Return whether a set of files are obsolete with respect to their former version."""
        # do some usage of the parameters to avoid linter warnings
        assert isinstance(state_ext, str)
        # consider a file is always obsolete
        return False

    def save_state(self, state_files: List[str], state_ext: str):
        """Store a ``md5`` value for a set of files."""
        for file in list(*state_files):
            assert isinstance(file, str)
        assert isinstance(state_ext, str)


# global instance
_stub = SCToCStub()


def reset_stub() -> SCToCStub:
    """Create a new stub instance."""
    global _stub

    _stub = SCToCStub()
    return _stub


def set_stub(new_stub: SCToCStub):
    """Set a new stub instance."""
    global _stub

    _stub = new_stub


def get_stub() -> SCToCStub:
    """Return the current stub instance."""
    return _stub


# interface
def _get_operator_sample_time() -> Tuple[float, float, bool]:
    return _stub.get_operator_sample_time()


def _get_list_of_project_files(*args, **kwargs) -> List[str]:
    return _stub.get_list_of_project_files(*args, **kwargs)


def _get_list_of_external_files(*kinds: str) -> List[str]:
    return _stub.get_list_of_project_files(*kinds)


# adding make directives
def _add_c_files(c_files: List[str], relative: bool, service: str):
    _stub.add_c_files(c_files, relative, service)


def _add_ada_files(ada_files: List[str], relative: bool, service: str):
    _stub.add_ada_files(ada_files, relative, service)


def _add_object_files(obj_files: List[str], relative: bool):
    _stub.add_object_files(obj_files, relative)


def _add_include_files(directories: List[str], relative: bool):
    _stub.add_include_files(directories, relative)


def _add_dynamic_library_rule(
    basename: str,
    c_files: List[str],
    o_files: List[str],
    def_files: List[str],
    dependencies: List[str],
    main: bool,
    cpu_type: str = '',
    language: str = '',
):
    _stub.add_dynamic_library_rule(
        basename, c_files, o_files, def_files, dependencies, main, cpu_type, language
    )


def _add_static_library_rule(
    basename: str, c_files: List[str], o_files: List[str], main: bool, cpu_type: str, language: str
):
    _stub.add_static_library_rule(basename, c_files, o_files, main, cpu_type, language)


def _add_executable_rule(
    basename: str,
    c_files: List[str],
    o_files: List[str],
    dependencies: List[str],
    main: bool,
    cpu_type: str = '',
    language: str = '',
):
    _stub.add_executable_rule(basename, c_files, o_files, dependencies, main, cpu_type, language)


def _add_custom_rule(
    basename: str,
    dependencies: List[str],
    commands: List[str],
    main: bool,
    cpu_type: str = '',
    language: str = '',
):
    _stub.add_custom_rule(basename, dependencies, commands, main, cpu_type, language)


def _add_variable(name: str, value: str):
    _stub.add_variable(name, value)


def _add_path_variable(name: str, value: str, relative: bool):
    _stub.add_path_variable(name, value, relative)


def _set_compiler_kind(kind: str):
    _stub.set_compiler_kind(kind)


def _add_preprocessor_definitions(*definitions: str):
    _stub.add_preprocessor_definitions(*definitions)


def _get_compiler_object_directory() -> str:
    return _stub.get_compiler_object_directory()


# sending feedback to SCADE Suite user interface
def _add_error(category: str, code: str, messages: List[Tuple[str, str]]):
    _stub.add_error(category, code, messages)


def _add_warning(category: str, code: str, messages: List[Tuple[str, str]]):
    _stub.add_warning(category, code, messages)


def _add_information(category: str, code: str, messages: List[Tuple[str, str]]):
    _stub.add_information(category, code, messages)


def _add_generated_files(service: str, files: List[str]):
    _stub.add_generated_files(service, files)


# misc. (undocumented)
def _is_state_up_to_date(state_ext: str) -> bool:
    return _stub.is_state_up_to_date(state_ext)


def _save_state(state_files: List[str], state_ext: str):
    _stub.save_state(state_files, state_ext)


# patch
# getting information from input project and model
sctoc.get_operator_sample_time = _get_operator_sample_time
sctoc.get_list_of_project_files = _get_list_of_project_files
sctoc.get_list_of_external_files = _get_list_of_external_files
# adding make directives
sctoc.add_c_files = _add_c_files
sctoc.add_ada_files = _add_ada_files
sctoc.add_object_files = _add_object_files
sctoc.add_include_files = _add_include_files
sctoc.add_dynamic_library_rule = _add_dynamic_library_rule
sctoc.add_static_library_rule = _add_static_library_rule
sctoc.add_executable_rule = _add_executable_rule
sctoc.add_custom_rule = _add_custom_rule
sctoc.add_variable = _add_variable
sctoc.add_path_variable = _add_path_variable
sctoc.set_compiler_kind = _set_compiler_kind
sctoc.add_preprocessor_definitions = _add_preprocessor_definitions
sctoc.get_compiler_object_directory = _get_compiler_object_directory
# sending feedback to SCADE Suite user interface
sctoc.add_error = _add_error
sctoc.add_warning = _add_warning
sctoc.add_information = _add_information
sctoc.add_generated_files = _add_generated_files
# misc. (undocumented)
sctoc.is_state_up_to_date = _is_state_up_to_date
sctoc.save_state = _save_state
