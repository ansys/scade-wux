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

from ansys.scade.wux import __version__
import ansys.scade.wux.impl.display as display
import ansys.scade.wux.impl.proxy as proxy
import ansys.scade.wux.wux as wux

# ----------------------------------------------------------------------------
# wrapper interface: class and methods
# ----------------------------------------------------------------------------


class SdyExt:
    """TODO."""

    ID = 'WUX2_SDY'
    tool = 'SCADE Suite-Display Extension'
    banner = '%s (WUX %s)' % (tool, __version__)

    script_path = Path(__file__)
    script_dir = script_path.parent

    # files
    sources = []

    @classmethod
    def init(cls, target_dir, project, configuration):
        """TODO."""
        cg = ('Code Generator', ('-Order', 'Before'))
        ctx = ('WUX2_CTX', ('-Order', 'Before'))
        return [cg, ctx]

    @classmethod
    def generate(cls, target_dir, project, configuration):
        """TODO."""
        print(cls.banner)

        roots = wux.mf.get_root_operators()

        # generation
        cls.generate_display(target_dir, project, configuration, roots, wux.ips)
        cls.generate_proxy_file(target_dir, project, configuration, roots)

        # build
        cls.declare_target(target_dir, project, configuration, roots)

        return True

    @classmethod
    def build(cls, target_dir, project, configuration):
        """TODO."""
        display.build(target_dir, project, configuration)
        return True

    # ----------------------------------------------------------------------------
    # wrapper implementation
    # ----------------------------------------------------------------------------

    @classmethod
    def generate_display(cls, target_dir, project, configuration, roots, ips):
        """TODO."""
        path = Path(project.pathname)
        pathname = Path(target_dir) / ('wuxsdy' + path.stem + '.c')
        sctoc.add_generated_files(cls.tool, [pathname.name])
        cls.sources.append(pathname)
        with open(str(pathname), 'w') as f:
            wux.gen_header(f, cls.banner)
            display.generate(f, target_dir, project, configuration, roots, ips)
            wux.gen_footer(f)

    @classmethod
    def generate_proxy_file(cls, target_dir, project, configuration, roots):
        """TODO."""
        path = Path(project.pathname)
        pathname = Path(target_dir) / ('wuxsdyprx' + path.stem + '.cpp')
        sctoc.add_generated_files(cls.tool, [pathname.name])
        cls.sources.append(pathname)
        with open(str(pathname), 'w') as f:
            wux.gen_header(f, cls.banner)
            proxy.generate(f, target_dir, project, configuration)
            wux.gen_footer(f)

    # ----------------------------------------------------------------------------
    # build
    # ----------------------------------------------------------------------------

    @classmethod
    def declare_target(cls, target_dir, project, configuration, roots):
        """TODO."""
        # runtime files
        include = cls.script_dir.parent / 'include'
        wux.add_includes([include])
        wux.add_sources(cls.sources)
        if display.get_specifications():
            lib = cls.script_dir.parent / 'lib'
            wux.add_sources([lib / 'WuxSdyProxy.cpp'])


# ----------------------------------------------------------------------------
# list of services
# ----------------------------------------------------------------------------


def get_services():
    """TODO."""
    scx = (
        SdyExt.ID,
        ('-OnInit', SdyExt.init),
        ('-OnGenerate', SdyExt.generate),
        ('-OnBuild', SdyExt.build),
    )
    return [scx]
