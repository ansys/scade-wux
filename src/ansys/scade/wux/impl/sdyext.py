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

"""Extension for reusable SCADE-Suite co-simulation wrapper."""

from pathlib import Path

import scade.code.suite.sctoc as sctoc
import scade.model.suite.displaycoupling as sdy

from ansys.scade.wux import __version__
import ansys.scade.wux.impl.display as display
import ansys.scade.wux.impl.proxy as proxy
import ansys.scade.wux.wux as wux

# ----------------------------------------------------------------------------
# wrapper interface: class and methods
# ----------------------------------------------------------------------------


class SdyExt:
    ID = 'WUX2_SDY'
    tool = 'SCADE Suite-Display Extension'
    banner = '%s (WUX %s)' % (tool, __version__)

    script_path = Path(__file__)
    script_dir = script_path.parent

    sdy_applications = sdy.get_roots()

    def __init__(self):
        # files
        self.sources = []

    @classmethod
    def get_service(cls):
        """Declare the generation service Python Wrapper."""
        cls.instance = SdyExt()
        scx = (
            cls.ID,
            ('-OnInit', cls.instance.init),
            ('-OnGenerate', cls.instance.generate),
            ('-OnBuild', cls.instance.build),
        )
        return scx

    def init(self, target_dir, project, configuration):
        cg = ('Code Generator', ('-Order', 'Before'))
        ctx = ('WUX2_CTX', ('-Order', 'Before'))
        return [cg, ctx]

    def generate(self, target_dir, project, configuration):
        print(self.banner)

        roots = wux.mf.get_root_operators()

        # generation
        self.generate_display(target_dir, project, configuration, roots, wux.ips)
        self.generate_proxy_file(target_dir, project, configuration, roots)

        # build
        self.declare_target(target_dir, project, configuration, roots)

        return True

    def build(self, target_dir, project, configuration):
        display.build(target_dir, project, configuration)
        return True

    # ----------------------------------------------------------------------------
    # wrapper implementation
    # ----------------------------------------------------------------------------

    def generate_display(self, target_dir, project, configuration, roots, ips):
        path = Path(project.pathname)
        pathname = Path(target_dir) / ('wuxsdy' + path.stem + '.c')
        sctoc.add_generated_files(self.tool, [pathname.name])
        self.sources.append(pathname)
        with open(str(pathname), 'w') as f:
            wux.gen_header(f, self.banner)
            display.generate(
                f, target_dir, project, configuration, roots, ips, self.sdy_applications
            )
            wux.gen_footer(f)

    def generate_proxy_file(self, target_dir, project, configuration, roots):
        path = Path(project.pathname)
        pathname = Path(target_dir) / ('wuxsdyprx' + path.stem + '.cpp')
        sctoc.add_generated_files(self.tool, [pathname.name])
        self.sources.append(pathname)
        with open(str(pathname), 'w') as f:
            wux.gen_header(f, self.banner)
            proxy.generate(f, target_dir, project, configuration)
            wux.gen_footer(f)

    # ----------------------------------------------------------------------------
    # build
    # ----------------------------------------------------------------------------

    def declare_target(self, target_dir, project, configuration, roots):
        # runtime files
        include = self.script_dir.parent / 'include'
        wux.add_includes([include])
        wux.add_sources(self.sources)
        if display.get_specifications():
            lib = self.script_dir.parent / 'lib'
            wux.add_sources([lib / 'WuxSdyProxy.cpp'])

        # make sure the linker option -static -lstdc++ is set for gcc
        wux.add_cpp_options(project, configuration)


# ----------------------------------------------------------------------------
# list of services
# ----------------------------------------------------------------------------


def get_services():
    return [SdyExt.get_service()]
