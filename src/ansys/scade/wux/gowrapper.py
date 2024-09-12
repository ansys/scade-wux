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
wrapper and the extensions is done through the global instance wux.
"""

from pathlib import Path

from scade.code.suite.mapping.c import MappingFile
import scade.code.suite.sctoc as sctoc
from scade.model.project.stdproject import Configuration, Project

from ansys.scade.wux import __version__
from ansys.scade.wux.wux import wux as _wux


class GoWrapper:
    """TODO."""

    # identification
    tool = 'Generic Integration'
    banner = '%s (WUX %s)' % (tool, __version__)

    script_path = Path(__file__)
    script_dir = script_path.parent

    @classmethod
    def get_services(cls):
        """TODO."""
        # ID meaningless, the service declared by this module
        # is involved automatically when the module is selected
        # in the Code Generator integration settings
        gowrp = (
            '<UNUSED WUX2_GO>',
            ('-OnInit', GoWrapper.init),
            ('-OnGenerate', GoWrapper.generate),
        )
        return [gowrp]

    @classmethod
    def init(cls, target_dir: str, project: Project, configuration: Configuration):
        """TODO."""
        sdy = ('WUX2_SDY', ('-Order', 'Before'))
        uua = ('WUX2_UAA', ('-Order', 'Before'))
        return [sdy, uua]

    @classmethod
    def generate(cls, target_dir: str, project: Project, configuration: Configuration):
        """TODO."""
        print(cls.banner)

        # build
        cls.declare_target(target_dir, project, configuration)

        return True

    @classmethod
    def get_target_exe(cls, target_dir, project, configuration) -> str:
        """TODO."""
        # wrapper utils
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
    def declare_target(cls, target_dir, project, configuration):
        """TODO."""
        # add the wrapper's main file
        lib = cls.script_dir / 'lib'
        _wux.add_sources([lib / 'WuxGoMain.cpp'])
        _wux.add_definitions('WUX_INTEGRATION', 'WUX_STANDALONE')
        # temporary hack: reuse the design developed for the so-simulation
        include = cls.script_dir / 'include'
        _wux.add_includes([include])
        _wux.add_sources([lib / 'WuxSimuExt.cpp'])

        # declare the target to sctoc
        path = cls.get_target_exe(target_dir, project, configuration)
        exts = ['Code Generator', 'WUX']
        # add the code generated by the selected extensions
        exts += project.get_tool_prop_def('GENERATOR', 'OTHER_EXTENSIONS', [], configuration)
        sctoc.add_executable_rule(path, [], [], exts, True)
