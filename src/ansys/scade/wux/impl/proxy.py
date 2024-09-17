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

from typing import List

import scade.model.suite.displaycoupling as sdy

from ansys.scade.wux.impl.display import get_specifications
from ansys.scade.wux.wux import writeln

# ----------------------------------------------------------------------------
# variables
# ----------------------------------------------------------------------------

_sdy_specifications: List[sdy.Specification] = []

# ----------------------------------------------------------------------------
# generation
# ----------------------------------------------------------------------------


def gen_includes(f):
    """TODO."""
    writeln(f, 0, '#include <windows.h>')
    writeln(f, 0, '#include <stdio.h>')
    writeln(f)
    if _sdy_specifications:
        writeln(f, 0, '// SCADE Display includes')
        writeln(f, 0, 'extern "C" {')
        writeln(f, 0, '#include "sdy/sdy_events.h"')
        for spec in _sdy_specifications:
            writeln(f, 0, '#include "sdy/{}.h"'.format(spec.prefix))
        writeln(f, 0, '}')
        writeln(f)
    writeln(f, 0, '// runtime')
    if _sdy_specifications:
        writeln(f, 0, '#include "WuxSdyProxy.h"')
    writeln(f, 0, '#include "WuxSdyExt.h"')
    writeln(f)


def gen_proxy_class(f, spec):
    """TODO."""
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


def gen_proxy_functions(f, spec):
    """TODO."""
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
            '    return LoadLayerPointer((PfnLayerFunction*)& m_pfnL_{1}, "{0}", "{1}");'.format(
                prefix, layer.name
            ),
        )
    else:
        writeln(
            f,
            0,
            '    BOOL bError = LoadLayerPointer((PfnLayerFunction*)& m_pfnL_{1}, "{0}", "{1}");'.format(
                prefix, spec.layers[0].name
            ),
        )
        for layer in spec.layers[1:-2]:
            writeln(
                f,
                0,
                '    bError = bError || LoadLayerPointer((PfnLayerFunction*)& m_pfnL_{1}, "{0}", "{1}");'.format(
                    prefix, layer.name
                ),
            )
        writeln(
            f,
            0,
            '    return bError || LoadLayerPointer((PfnLayerFunction*)& m_pfnL_{1}, "{0}", "{1}");'.format(
                prefix, spec.layers[-1].name
            ),
        )
    writeln(f, 0, '}')
    writeln(f)
    for layer in spec.layers:
        writeln(f, 0, '{0}_typ_{1}* {0}_L_{1}()'.format(prefix, layer.name))
        writeln(f, 0, '{')
        writeln(f, 0, '    return h{0}.L_{1}();'.format(prefix, layer.name))
        writeln(f, 0, '}')
        writeln(f, 0, '')


def gen_instances(f):
    """TODO."""
    if _sdy_specifications:
        writeln(
            f,
            0,
            '#define SDY_PROC(RETURN,PREFIX,NAME,SIG,ARGS) DEF_SDY_DLL_PROC(RETURN,PREFIX,NAME,SIG,ARGS)',
        )
        for spec in _sdy_specifications:
            writeln(f, 0, 'DEF_SDY_DLL_INSTANCE({0})'.format(spec.prefix))
        writeln(f, 0, '#undef SDY_PROC')
        writeln(f)


def gen_load(f):
    """TODO."""
    writeln(f, 0, 'int WuxLoadSdyDlls(/*HINSTANCE*/ void* hinstDll)')
    writeln(f, 0, '{')
    if _sdy_specifications:
        writeln(f, 0, '    BOOL bSuccess = TRUE;')
        for spec in _sdy_specifications:
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


def gen_unload(f):
    """TODO."""
    writeln(f, 0, 'int WuxUnloadSdyDlls(/*HINSTANCE*/ void* hinstDll)')
    writeln(f, 0, '{')
    if _sdy_specifications:
        writeln(f, 0, '    BOOL bSuccess = TRUE;')
        for spec in _sdy_specifications:
            writeln(f, 1, 'if (bSuccess) bSuccess = h{0}.Unload();'.format(spec.prefix))
        writeln(f, 0, '    return bSuccess == TRUE;')
    else:
        writeln(f, 0, '    return 1;')
    writeln(f, 0, '}')
    writeln(f)


def generate(f, target_dir, project, configuration):
    """TODO."""
    global _sdy_specifications

    _sdy_specifications = get_specifications()

    gen_includes(f)
    for spec in _sdy_specifications:
        gen_proxy_class(f, spec)
    gen_instances(f)
    for spec in _sdy_specifications:
        gen_proxy_functions(f, spec)
    gen_load(f)
    gen_unload(f)
