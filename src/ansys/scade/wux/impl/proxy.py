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

"""Proxies to the SCADE Display DLLs."""

import os
from pathlib import Path
import subprocess
import sys
from typing import List

import scade.code.suite.sctoc as sctoc
import scade.model.suite.displaycoupling as sdy

from ansys.scade.apitools.info import get_scade_home
from ansys.scade.wux import __version__
import ansys.scade.wux.wux as wux

# from ansys.scade.wux.impl.display import get_specifications
from ansys.scade.wux.wux import writeln

# ----------------------------------------------------------------------------
# wrapper interface: class and methods
# ----------------------------------------------------------------------------


class SdyProxyExt:
    ID = 'WUX2_SDY_PROXY'
    tool = 'SCADE Display Proxy Extension'
    banner = '%s (WUX %s)' % (tool, __version__)

    script_path = Path(__file__)
    script_dir = script_path.parent

    def __init__(self):
        # specifications
        self.specifications: List[sdy.Specification] = []
        # files
        self.sources = []

    @classmethod
    def get_service(cls):
        """Declare the generation service SCADE Suite-Display Extension."""
        cls.instance = SdyProxyExt()
        scx = (
            cls.ID,
            ('-OnInit', cls.instance.init),
            ('-OnGenerate', cls.instance.generate),
            ('-OnBuild', cls.instance.build),
        )
        return scx

    def init(self, target_dir, project, configuration):
        return []

    def generate(self, target_dir, project, configuration):
        print(self.banner)

        self.specifications = wux.get_specifications(project, configuration)

        path = Path(project.pathname)
        pathname = Path(target_dir) / ('wuxsdyprx' + path.stem + '.cpp')
        sctoc.add_generated_files(self.tool, [pathname.name])
        self.sources.append(pathname)
        with open(str(pathname), 'w') as f:
            wux.gen_header(f, self.banner)
            self.gen_includes(f)
            for spec in self.specifications:
                self.gen_proxy_class(f, spec)
            self.gen_instances(f)
            for spec in self.specifications:
                self.gen_proxy_functions(f, spec)
            self.gen_load(f)
            self.gen_unload(f)
            wux.gen_footer(f)

        return True

    def build(self, target_dir, project, configuration):
        ansys_scade_dir = get_scade_home()
        sdy_display_home = str(ansys_scade_dir / 'SCADE Display')
        sdy_rapidproto_home = str(ansys_scade_dir / 'SCADE Test' / 'Rapid Prototyper')

        ok = True
        # generate in a sub directory to not have the header files deleted by
        # the generation process (bourrin) prior any generation
        sdy_target_dir = target_dir + '/sdy'
        try:
            os.mkdir(sdy_target_dir)
        except FileExistsError:
            pass
        # return ok
        for spec in self.specifications:
            sdy_project = os.path.abspath(spec.sdy_project.pathname)
            prefix = spec.prefix
            log = os.path.join(os.path.abspath(sdy_target_dir), prefix + '.log')
            # path of the dll generated by SCADE Display/RP
            sdydll = os.path.join(os.path.abspath(sdy_target_dir), prefix + '.dll')
            # path of the dll once moved to target_dir
            dll = os.path.join(os.path.abspath(target_dir), prefix + '.dll')
            state_ext = 'wux_' + prefix
            up_to_date = sctoc.is_state_up_to_date(state_ext)
            state_files = sctoc.get_list_of_project_files([], sdy_project, spec.conf)
            state_files.append(dll)

            # Generate
            if spec.sdy_project.is_rapid_proto():
                exe = '{}\\bin\\ScadeRP.exe'.format(sdy_rapidproto_home)
            else:
                exe = '{}\\bin\\ScadeDisplayConsole.exe'.format(sdy_display_home)
            try:
                if up_to_date:
                    print('Skipping up_to_date graphical panel {}'.format(prefix))
                    sctoc.add_generated_files('Graphical Panels', [Path(dll).name])
                else:
                    print('Generating graphical panel {}...'.format(prefix))
                    with open(log, 'w') as lf:
                        cmd = [
                            exe,
                            'batch',
                            'generate',
                            sdy_project,
                            '-conf',
                            spec.conf,
                            '-source',
                            spec.get_name(),
                            '-outdir',
                            os.path.abspath(sdy_target_dir),
                            '-prefix',
                            prefix,
                        ]
                        subprocess.call(cmd, stdout=lf, stderr=lf)
                    if os.path.isfile(sdydll):
                        os.replace(sdydll, dll)
                        sctoc.add_generated_files('Graphical Panels', [Path(dll).name])
                        # sctoc.add_object_files([archive], False)
                        print('Generation successful for {}.'.format(prefix))
                        sctoc.save_state(state_files, state_ext)
                    else:
                        ok = False
                        print('Generation failed for {}.'.format(prefix))
            except BaseException:
                ok = False
                print('Unexpected error:', sys.exc_info()[0])
        if ok:
            other_dlls = ['d3dcompiler_47.dll', 'libEGL.dll', 'libGLESv2.dll']
            for dll in other_dlls:
                sdydll = os.path.join(os.path.abspath(sdy_target_dir), dll)
                if os.path.isfile(sdydll):
                    dll = os.path.join(os.path.abspath(target_dir), dll)
                    os.replace(sdydll, dll)
                if os.path.isfile(dll):
                    sctoc.add_generated_files('Graphical Panels', [Path(dll).name])

        self.declare_target(target_dir, project, configuration)
        return True

    # ----------------------------------------------------------------------------
    # generation
    # ----------------------------------------------------------------------------

    def gen_includes(self, f):
        writeln(f, 0, '#include <windows.h>')
        writeln(f, 0, '#include <stdio.h>')
        writeln(f)
        if self.specifications:
            writeln(f, 0, '// SCADE Display includes')
            writeln(f, 0, 'extern "C" {')
            writeln(f, 0, '#include "sdy/sdy_events.h"')
            for spec in self.specifications:
                writeln(f, 0, '#include "sdy/{}.h"'.format(spec.prefix))
            writeln(f, 0, '}')
            writeln(f)
        writeln(f, 0, '// runtime')
        if self.specifications:
            writeln(f, 0, '#include "WuxSdyDll.h"')
        writeln(f, 0, '#include "WuxSdyProxy.h"')
        writeln(f)

    def gen_proxy_class(self, f, spec):
        prefix = spec.prefix
        writeln(f, 0, 'class C{0}DllProxy : public CSdyDllProxy'.format(prefix))
        writeln(f, 0, '{')
        writeln(f, 0, 'public:')
        for layer in spec.layers:
            writeln(f, 0, '    inline {0}_typ_{1}* L_{1}()'.format(prefix, layer.name))
            writeln(f, 0, '    {')
            writeln(f, 0, '	return m_pfnL_{0}();'.format(layer.name))
            writeln(f, 0, '    }')
        writeln(f, 0, 'protected:')
        writeln(f, 0, '    virtual void ZeroPointers();')
        writeln(f, 0, '    virtual BOOL LoadLayerPointers();')
        for layer in spec.layers:
            writeln(f, 0, '    {0}_typ_{1}* (*m_pfnL_{1})();'.format(prefix, layer.name))
        writeln(f, 0, '};')
        writeln(f)

    def gen_proxy_functions(self, f, spec):
        prefix = spec.prefix
        writeln(f, 0, 'void C{0}DllProxy::ZeroPointers()'.format(prefix))
        writeln(f, 0, '{')
        writeln(f, 0, '    CSdyDllProxy::ZeroPointers();')
        for layer in spec.layers:
            writeln(f, 0, '    m_pfnL_{0} = NULL;'.format(layer.name))
        writeln(f, 0, '}')
        writeln(f)
        writeln(f, 0, 'BOOL C{0}DllProxy::LoadLayerPointers()'.format(prefix))
        writeln(f, 0, '{')
        if len(spec.layers) == 1:
            writeln(
                f,
                0,
                '    return LoadLayerPointer((PfnLayerFunction*)& '
                'm_pfnL_{1}, "{0}", "{1}");'.format(prefix, layer.name),
            )
        else:
            writeln(
                f,
                0,
                '    BOOL bError = LoadLayerPointer((PfnLayerFunction*)& '
                'm_pfnL_{1}, "{0}", "{1}");'.format(prefix, spec.layers[0].name),
            )
            for layer in spec.layers[1:-2]:
                writeln(
                    f,
                    0,
                    '    bError = bError || LoadLayerPointer((PfnLayerFunction*)& '
                    'm_pfnL_{1}, "{0}", "{1}");'.format(prefix, layer.name),
                )
            writeln(
                f,
                0,
                '    return bError || LoadLayerPointer((PfnLayerFunction*)& '
                'm_pfnL_{1}, "{0}", "{1}");'.format(prefix, spec.layers[-1].name),
            )
        writeln(f, 0, '}')
        writeln(f)
        for layer in spec.layers:
            writeln(f, 0, '{0}_typ_{1}* {0}_L_{1}()'.format(prefix, layer.name))
            writeln(f, 0, '{')
            writeln(f, 0, '    return h{0}.L_{1}();'.format(prefix, layer.name))
            writeln(f, 0, '}')
            writeln(f, 0, '')

    def gen_instances(self, f):
        if self.specifications:
            writeln(
                f,
                0,
                '#define SDY_PROC(RETURN,PREFIX,NAME,SIG,ARGS) '
                'DEF_SDY_DLL_PROC(RETURN,PREFIX,NAME,SIG,ARGS)',
            )
            for spec in self.specifications:
                writeln(f, 0, 'DEF_SDY_DLL_INSTANCE({0})'.format(spec.prefix))
            writeln(f, 0, '#undef SDY_PROC')
            writeln(f)

    def gen_load(self, f):
        writeln(f, 0, 'int WuxLoadSdyDlls(/*HINSTANCE*/ void* hinstDll)')
        writeln(f, 0, '{')
        if self.specifications:
            writeln(f, 0, '    BOOL bSuccess = TRUE;')
            for spec in self.specifications:
                writeln(
                    f,
                    1,
                    'if (bSuccess) bSuccess = h{0}.Load((HINSTANCE)hinstDll, "{0}");'.format(
                        spec.prefix
                    ),
                )
            writeln(f, 0, '    return bSuccess == TRUE;')
        else:
            writeln(f, 0, '    return 1;')
        writeln(f, 0, '}')
        writeln(f)

    def gen_unload(self, f):
        writeln(f, 0, 'int WuxUnloadSdyDlls(/*HINSTANCE*/ void* hinstDll)')
        writeln(f, 0, '{')
        if self.specifications:
            writeln(f, 0, '    BOOL bSuccess = TRUE;')
            for spec in self.specifications:
                writeln(f, 1, 'if (bSuccess) bSuccess = h{0}.Unload();'.format(spec.prefix))
            writeln(f, 0, '    return bSuccess == TRUE;')
        else:
            writeln(f, 0, '    return 1;')
        writeln(f, 0, '}')
        writeln(f)

    # ----------------------------------------------------------------------------
    # build
    # ----------------------------------------------------------------------------

    def declare_target(self, target_dir, project, configuration):
        # runtime files
        include = self.script_dir.parent / 'include'
        wux.add_includes([include])
        wux.add_sources(self.sources)
        if self.specifications:
            lib = self.script_dir.parent / 'lib'
            wux.add_sources([lib / 'WuxSdyProxy.cpp'])

        # make sure the linker option -static -lstdc++ is set for gcc
        wux.add_cpp_options(project, configuration)


# ----------------------------------------------------------------------------
# list of services
# ----------------------------------------------------------------------------


def get_services():
    return [SdyProxyExt.get_service()]
