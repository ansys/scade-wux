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

"""Share DllMain to the registered extensions: no code is generated."""

from pathlib import Path

from scade.model.project.stdproject import Configuration, Project

from ansys.scade.wux import __version__
import ansys.scade.wux.wux as wux


class WuxDllExt:
    """TODO."""

    ID = 'WUX2_DLL_EXT'
    tool = 'Support for sharing DllMain'
    banner = '%s (WUX %s)' % (tool, __version__)

    script_path = Path(__file__)
    script_dir = script_path.parent

    @classmethod
    def init(cls, target_dir: str, project: Project, configuration: Configuration):
        """TODO."""
        return []

    @classmethod
    def generate(cls, target_dir: str, project: Project, configuration: Configuration):
        """TODO."""
        print(cls.banner)

        # always add the files, to ease the integration
        # runtime files
        include = cls.script_dir.parent / 'include'
        wux.add_includes([include])
        lib = cls.script_dir.parent / 'lib'
        wux.add_sources([lib / 'WuxDllExt.cpp'])

        return True


# ----------------------------------------------------------------------------
# list of services
# ----------------------------------------------------------------------------


def get_services():
    """TODO."""
    wux_ctx = (WuxDllExt.ID, ('-OnInit', WuxDllExt.init), ('-OnGenerate', WuxDllExt.generate))
    return [wux_ctx]
