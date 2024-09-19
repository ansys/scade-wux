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
Patch simulator's interface file for allowing multiple hooks.

The interface file allows only one hook, ``EXTENDED_SIM``.
This enhancement replaces the calls to a custom hook that can hold several hooks.
"""

import os
from pathlib import Path

from scade.model.project.stdproject import Configuration, Project

from ansys.scade.wux import __version__
import ansys.scade.wux.wux as wux


class WuxSimuExt:
    """
    Generator service for the integration (``WUX2_SIMU_EXT``).

    * Patch the ``xxx_interface.c`` file from the SCADE Simulator
      to replace the hooks
    """

    ID = 'WUX2_SIMU_EXT'
    tool = "Extension for Simulator's extensions"
    banner = '%s (WUX %s)' % (tool, __version__)
    # prefix of genetared files
    PREFIX = 'wuxsmu'

    script_path = Path(__file__)
    script_dir = script_path.parent

    # options, may be overridden by clients
    simulation = False

    @classmethod
    def init(cls, target_dir: str, project: Project, configuration: Configuration):
        # check simulation mode
        cls.set_simulation(project, configuration)
        # if the simulator in involved, it must be executed before
        if cls.simulation:
            simu = ('Simulator Wrapper', ('-Order', 'Before'))
            return [simu]
        else:
            return []

    @classmethod
    def generate(cls, target_dir: str, project: Project, configuration: Configuration):
        if not cls.simulation:
            return True

        print(cls.banner)

        # patch the interface file
        # . include WuxSimuExt.h
        # . Prefix all EXTENDED_SIM function calls by Wux

        functions = [
            'BeforeSimInit',
            'AfterSimInit',
            'BeforeSimStep',
            'AfterSimStep',
            'ExtendedSimStop',
            'ExtendedGatherDumpData',
            'ExtendedRestoreDumpData',
            'ExtendedGetDumpSize',
            'UpdateValues',
            'UpdateSimulatorValues',
        ]

        basename = Path(project.pathname).stem + '_interface'
        pathname = (Path(target_dir) / basename).with_suffix('.c')
        tmp = pathname.with_suffix('.tmp')
        try:
            f_in = pathname.open('r')
        except FileNotFoundError:
            print('cannot patch %s for simulation extension' % pathname)
            return True

        f_out = tmp.open('w')
        f_out.write('#include "WuxSimuExt.h"\n')

        # EXTENDED_SIM is set iff graphical panels are involved:
        # instead of removing the hooks, it is much easier to define locally the name
        f_out.write('#ifndef EXTENDED_SIM\n')
        f_out.write('#define EXTENDED_SIM\n')
        f_out.write('#endif\n')
        idle = True
        for line in f_in:
            if idle:
                if '#ifdef EXTENDED_SIM' in line:
                    idle = False
            else:
                if line[0] == '#':
                    idle = True
                else:
                    for function in functions:
                        line = line.replace(function, 'Wux' + function)
            f_out.write(line)
        f_in.close()
        f_out.close()
        os.replace(tmp, pathname)

        # always add the files, to ease the integration
        # runtime files
        include = cls.script_dir.parent / 'include'
        wux.add_includes([include])
        lib = cls.script_dir.parent / 'lib'
        wux.add_sources([lib / 'WuxSimuExt.cpp'])

        return True

    @classmethod
    def set_simulation(cls, project: Project, configuration: Configuration):
        enable_extensions = project.get_bool_tool_prop_def(
            'GENERATOR', 'ENABLE_EXTENSIONS', True, configuration
        )
        target = project.get_scalar_tool_prop_def(
            'GENERATOR', 'TARGET_ADAPTOR', 'Simulator', configuration
        )
        cls.simulation = enable_extensions and target == 'Simulator'


# ----------------------------------------------------------------------------
# list of services
# ----------------------------------------------------------------------------


def get_services():
    """Return the list of Generation services implemented by this module."""
    wux_ctx = (WuxSimuExt.ID, ('-OnInit', WuxSimuExt.init), ('-OnGenerate', WuxSimuExt.generate))
    return [wux_ctx]
