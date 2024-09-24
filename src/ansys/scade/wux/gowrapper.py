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

"""
Generic wrapper for hosting combined SCADE Suite integration extensions.

* 99% of the generation is ensured by the extensions
* The wrapper declares the target

Design note: the core extensions register to this wrapper which gathers the
makefile elements to build the executable. The communication between the
wrapper and the extensions is done through the global variables of
the ``wux`` module.
"""

from pathlib import Path

from scade.code.suite.mapping.c import MappingFile
import scade.code.suite.sctoc as sctoc
from scade.model.project.stdproject import Configuration, Project

from ansys.scade.wux import __version__
import ansys.scade.wux.wux as wux


class GoWrapper:
    """
    Implements the *Generic Integration* (``WUX2_GOWRP``) generation module.

    Refer to :ref:`Wrapper <usage/wrapper:wrapper>` to for its usage.

    Refer to *Generation Module* in the User Documentation,
    section *3/ Code Integration Toolbox/Declaring Code Generator Extension*.
    """

    # identification
    _tool = 'Generic Integration'
    _banner = '%s (WUX %s)' % (_tool, __version__)

    _script_path = Path(__file__)
    _script_dir = _script_path.parent

    @classmethod
    def get_services(cls):
        """Declare the generation service GoWrapper."""
        # the ID is meaningless, the service declared by this module
        # is activated automatically when the module is selected
        # in the Code Generator integration settings
        gowrp = (
            '<UNUSED WUX2_GO>',
            ('-OnInit', GoWrapper.init),
            ('-OnGenerate', GoWrapper.generate),
        )
        return [gowrp]

    @classmethod
    def init(cls, target_dir: str, project: Project, configuration: Configuration):
        """
        Declare the required generation services and the execution order.

        Refer to *Generation Service* in the User Documentation,
        section *3/ Code Integration Toolbox/Declaring Code Generator Extension*.

        Parameters
        ----------
        target_dir : str
            Target directory for the code generation.

        project : Project
            Input SCADE Suite project.

        configuration : configuration
            SCADE Suite configuration selected for the code generation.
        """
        sdy = ('WUX2_SDY', ('-Order', 'Before'))
        uua = ('WUX2_UAA', ('-Order', 'Before'))
        return [sdy, uua]

    @classmethod
    def generate(cls, target_dir: str, project: Project, configuration: Configuration):
        """
        Generate the code for this generation service.

        Refer to *Generation Service* in the User Documentation,
        section *3/ Code Integration Toolbox/Declaring Code Generator Extension*.

        Parameters
        ----------
        target_dir : str
            Target directory for the code generation.

        project : Project
            Input SCADE Suite project.

        configuration : configuration
            SCADE Suite configuration selected for the code generation.
        """
        print(cls._banner)

        # build
        cls._declare_target(target_dir, project, configuration)

        return True

    @classmethod
    def _get_target_exe(cls, target_dir, project, configuration) -> str:
        # return the name of the binary expected by the SCADE IDE
        # Code Generator by replicating its algorithm
        mf = MappingFile((Path(target_dir) / 'mapping.xml').as_posix())
        roots = mf.get_root_operators()

        # path = '_'.join(list(map(lambda x: x.get_name(), roots)))
        root = sorted(roots, key=lambda x: x.get_name())[0]
        path = [root.get_name()]
        package = root.get_package()
        while not package.is_root():
            path.append(package.get_name())
            package = package.get_package()
        path.reverse()
        path = '__'.join(path)
        return path

    @classmethod
    def _declare_target(cls, target_dir, project, configuration):
        # add the wrapper's main file
        lib = cls._script_dir / 'lib'
        wux.add_sources([lib / 'WuxGoMain.cpp'])
        wux.add_definitions('WUX_INTEGRATION', 'WUX_STANDALONE')
        # temporary hack: reuse the design developed for the co-simulation
        include = cls._script_dir / 'include'
        wux.add_includes([include])
        wux.add_sources([lib / 'WuxSimuExt.cpp'])

        # declare the target to sctoc
        path = cls._get_target_exe(target_dir, project, configuration)
        exts = ['Code Generator', 'WUX']
        # add the code generated by the selected extensions
        exts += project.get_tool_prop_def('GENERATOR', 'OTHER_EXTENSIONS', [], configuration)
        sctoc.add_executable_rule(path, [], [], exts, True)

        # make sure the linker option -static -lstdc++ is set for gcc
        # the following statements modify the project file, which is fine since it
        # is not expected to be saved
        compiler = project.get_scalar_tool_prop_def('SIMULATOR', 'COMPILER', 'GNU C', configuration)
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
