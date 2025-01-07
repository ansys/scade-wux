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

"""Share DllMain to the registered extensions: no code is generated."""

from pathlib import Path

from scade.model.project.stdproject import Configuration, Project

from ansys.scade.wux import __version__
import ansys.scade.wux.wux as wux


class WuxDllExt:
    """Generation service for the integration (``WUX2_DLL_EXT``)."""

    ID = 'WUX2_DLL_EXT'
    tool = 'Support for sharing DllMain'
    banner = '%s (WUX %s)' % (tool, __version__)

    script_path = Path(__file__)
    script_dir = script_path.parent

    @classmethod
    def get_service(cls):
        """Declare the generation service DllMain extension."""
        cls.instance = WuxDllExt()
        dll = (cls.ID, ('-OnInit', cls.instance.init), ('-OnGenerate', cls.instance.generate))
        return dll

    def init(self, target_dir: str, project: Project, configuration: Configuration):
        """Initialize the generation service."""
        return []

    def generate(self, target_dir: str, project: Project, configuration: Configuration):
        """Generate the files."""
        print(self.banner)

        # always add the files, to ease the integration
        # runtime files
        include = self.script_dir.parent / 'include'
        wux.add_includes([include])
        lib = self.script_dir.parent / 'lib'
        wux.add_sources([lib / 'WuxDllExt.cpp'])

        # make sure the linker option -static -lstdc++ is set for gcc
        wux.add_cpp_options(project, configuration)

        return True


# ----------------------------------------------------------------------------
# list of services
# ----------------------------------------------------------------------------


def get_services():
    """Return the list of Generation services implemented by this module."""
    return [WuxDllExt.get_service()]
