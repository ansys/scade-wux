# Copyright (C) 2020 - 2026 ANSYS, Inc. and/or its affiliates.
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

"""Unit tests for kcgcontext.py."""

from io import StringIO
from pathlib import Path
import shutil

import pytest
import scade.model.project.stdproject as std

import ansys.scade.wux.impl.kcgcontext as wux_ctx
from ansys.scade.wux.impl.kcgcontext import WuxContext
from ansys.scade.wux.test.sctoc_stub import get_stub
from ansys.scade.wux.test.utils import ServiceProxy, reset_test_env
import ansys.scade.wux.wux as wux
from conftest import load_project


@pytest.fixture(scope='session')
def ut_kcg_context() -> std.Project:
    """Load the project."""
    path = Path(__file__).parent / 'UT' / 'KcgContext' / 'KcgContext.etp'
    return load_project(path)


def test_kcgcontext_ut_kcg(ut_kcg_context):
    project = ut_kcg_context
    configuration = project.find_configuration('UT KCG')
    assert configuration
    target_dir = Path(project.pathname).parent / configuration.name

    reset_test_env()
    ctx = WuxContext()
    ctx.set_simulation(project, configuration)
    assert not ctx.simulation
    ctx.set_globals(str(target_dir), project, configuration)
    # mf must be initialized
    assert wux.mf
    # sanity check: test on of the functions
    roots = {_.get_name() for _ in wux.mf.get_root_operators()}
    assert roots == {'Function', 'Node'}
    # as well as mh
    assert wux.mh
    # sanity check: test on of the functions
    sensors = {_ for _ in wux.mh.get_sensors()}
    assert sensors == {'P::reference', 'P::speed'}
    # as well as ips
    assert wux.ips
    roots = {_.get_operator().get_name() for _ in wux.ips}
    assert roots == {'Function', 'Node'}

    f = StringIO()
    ctx.gen_kcg_includes(f)
    text = f.getvalue()
    includes = {_.strip() for _ in text.strip(' \n').split('\n') if _ and _.strip()[:2] != '/*'}
    assert includes == {
        '#include "Function_P.h"',
        '#include "Node_P.h"',
        '#include "kcg_sensors.h"',
    }
    f.close()

    f = StringIO()
    ctx.gen_contexts_declaration(f, project)
    text = f.getvalue()
    # no unit test: output not regular
    # --> cf. test_kcgcontext_ut_node with a smaller text
    assert text
    f.close()

    f = StringIO()
    ctx.gen_contexts_definition(f)
    text = f.getvalue()
    definitions = {_.strip() for _ in text.strip('\n').split('\n') if _ and _.strip()[:2] != '/*'}
    assert definitions == {
        'WU_Function_P Wu_Ctx_Function_P;',
        'WU_Node_P Wu_Ctx_Node_P;',
    }
    f.close()

    f = StringIO()
    ctx.gen_sensors(f)
    text = f.getvalue()
    sensors = {_.strip() for _ in text.strip('\n').split('\n') if _ and _.strip()[:2] != '/*'}
    assert sensors == {
        'kcg_float32 speed_P;',
        'Position_P reference_P;',
    }
    f.close()

    f = StringIO()
    ctx.gen_init(f)
    text = f.getvalue()
    # no unit test: output not regular
    # --> cf. test_kcgcontext_ut_node with a smaller text
    assert text
    f.close()

    f = StringIO()
    ctx.gen_cycles(f)
    text = f.getvalue()
    # no unit test: output not regular
    # --> cf. test_kcgcontext_ut_node with a smaller text
    assert text
    f.close()

    f = StringIO()
    ctx.gen_period(f)
    text = f.getvalue()
    reference = '\n'.join(
        [
            'double WuxGetPeriod()',
            '{',
            '    return 0.02;',
            '}',
        ]
    )
    assert text.strip('\n') == reference
    f.close()


def test_kcgcontext_ut_simulation(ut_kcg_context):
    project = ut_kcg_context
    configuration = project.find_configuration('UT Simulation')
    assert configuration
    target_dir = Path(project.pathname).parent / configuration.name

    ctx = WuxContext()
    ctx.set_simulation(project, configuration)
    assert ctx.simulation
    ctx.set_globals(str(target_dir), project, configuration)
    # mf must be initialized
    assert wux.mf
    # sanity check: test on of the functions
    roots = {_.get_name() for _ in wux.mf.get_root_operators()}
    assert roots == {'Node'}
    # as well as mh
    assert wux.mh
    # sanity check: test on of the functions
    sensors = {_ for _ in wux.mh.get_sensors()}
    assert sensors == {'P::speed'}
    # as well as ips
    assert wux.ips
    roots = {_.get_operator().get_name() for _ in wux.ips}
    assert roots == {'Node'}

    f = StringIO()
    ctx.gen_kcg_includes(f)
    text = f.getvalue()
    includes = {_.strip() for _ in text.strip(' \n').split('\n') if _.strip()[:2] != '/*'}
    assert includes == {
        '#include "Node_P.h"',
        '#include "kcg_sensors.h"',
    }
    f.close()

    f = StringIO()
    ctx.gen_contexts_declaration(f, project)
    text = f.getvalue()
    declarations = {_.strip() for _ in text.strip('\n').split('\n') if _ and _.strip()[:2] != '/*'}
    assert declarations == {'#include "KcgContext_interface.h"'}
    f.close()

    f = StringIO()
    ctx.gen_contexts_definition(f)
    text = f.getvalue()
    definitions = {_.strip() for _ in text.strip('\n').split('\n') if _ and _.strip()[:2] != '/*'}
    assert not definitions
    f.close()

    f = StringIO()
    ctx.gen_sensors(f)
    text = f.getvalue()
    sensors = {_.strip() for _ in text.strip('\n').split('\n') if _ and _.strip()[:2] != '/*'}
    assert not sensors
    f.close()

    f = StringIO()
    ctx.gen_init(f)
    text = f.getvalue()
    reference = '\n'.join(
        [
            '/* initializations */',
            'void WuxReset()',
            '{',
            '}',
            '',
            'void WuxInit()',
            '{',
            '}',
        ]
    )
    assert text.strip('\n') == reference
    f.close()

    f = StringIO()
    ctx.gen_cycles(f)
    text = f.getvalue()
    reference = '\n'.join(
        [
            'void WuxCycle()',
            '{',
            '}',
        ]
    )
    assert text.strip('\n') == reference
    f.close()

    f = StringIO()
    ctx.gen_period(f)
    text = f.getvalue()
    reference = '\n'.join(
        [
            'double WuxGetPeriod()',
            '{',
            '    return 0.02;',
            '}',
        ]
    )
    assert text.strip('\n') == reference
    f.close()

    # extended IP
    ip = wux.ips[0]
    io = ip.get_generated_path('P::Node/origin/')
    assert io == 'inputs_ctx.origin'
    io = ip.get_generated_path('P::Node/out/')
    assert io == 'outputs_ctx.out'
    io = ip.get_generated_path('P::speed/')
    assert io == '_ctx_speed_P_buffer'
    # extended ip, cf. kcgcontext.py
    var = ip.get_in_context_var()  # type: ignore
    assert var == 'inputs_ctx'
    # extended ip, cf. kcgcontext.py
    var = ip.get_out_context_var()  # type: ignore
    assert var == 'outputs_ctx'


def test_kcgcontext_ut_node(ut_kcg_context):
    # comparable to ut_kcg
    # only one root operator to test large functions
    project = ut_kcg_context
    configuration = project.find_configuration('UT Node')
    assert configuration
    target_dir = Path(project.pathname).parent / configuration.name

    ctx = WuxContext()
    ctx.set_simulation(project, configuration)
    assert not ctx.simulation
    ctx.set_globals(str(target_dir), project, configuration)
    # mf, mh, ips must be initialized
    assert wux.mf
    assert wux.mh
    assert wux.ips

    f = StringIO()
    ctx.gen_contexts_declaration(f, project)
    text = f.getvalue()
    reference = '\n'.join(
        [
            '/* contexts */',
            'typedef struct {',
            '    outC_Node_P outC;',
            '    inC_Node_P inC;',
            '} WU_Node_P;',
            '',
            'extern WU_Node_P Wu_Ctx_Node_P;',
        ]
    )
    assert text.strip('\n') == reference
    f.close()

    f = StringIO()
    ctx.gen_contexts_definition(f)
    text = f.getvalue()
    definitions = set(text.strip('\n').split('\n'))
    assert definitions == {
        '/* contexts */',
        'WU_Node_P Wu_Ctx_Node_P;',
    }
    f.close()

    f = StringIO()
    ctx.gen_init(f)
    text = f.getvalue()
    reference = '\n'.join(
        [
            '/* initializations */',
            'void WuxReset()',
            '{',
            '}',
            '',
            'void WuxInit()',
            '{',
            '#   ifndef KCG_USER_DEFINED_INIT',
            '    Node_init_P(&Wu_Ctx_Node_P.outC);',
            '#   else',
            '#   ifndef KCG_NO_EXTERN_CALL_TO_RESET',
            '    Node_reset_P(&Wu_Ctx_Node_P.outC);',
            '#   endif /* KCG_NO_EXTERN_CALL_TO_RESET */',
            '#   endif /* KCG_USER_DEFINED_INIT */',
            '}',
        ]
    )
    assert text.strip('\n') == reference
    f.close()

    f = StringIO()
    ctx.gen_cycles(f)
    text = f.getvalue()
    reference = '\n'.join(
        [
            'void WuxCycle()',
            '{',
            '    Node_P(&Wu_Ctx_Node_P.inC, &Wu_Ctx_Node_P.outC);',
            '}',
        ]
    )
    assert text.strip('\n') == reference
    f.close()

    # extended IP
    ip = wux.ips[0]
    io = ip.get_generated_path('P::Node/origin/')
    assert io == 'Wu_Ctx_Node_P.inC.origin'
    io = ip.get_generated_path('P::Node/out/')
    assert io == 'Wu_Ctx_Node_P.outC.out'
    io = ip.get_generated_path('P::speed/')
    assert io == 'speed_P'
    # extended ip, cf. kcgcontext.py
    var = ip.get_in_context_var()  # type: ignore
    assert var == 'Wu_Ctx_Node_P.inC'
    # extended ip, cf. kcgcontext.py
    var = ip.get_out_context_var()  # type: ignore
    assert var == 'Wu_Ctx_Node_P.outC'


def test_kcgcontext_ut_global(ut_kcg_context):
    # comparable to ut_kcg
    # only one root operator to test large functions
    project = ut_kcg_context
    configuration = project.find_configuration('UT Global')
    assert configuration
    target_dir = Path(project.pathname).parent / configuration.name

    ctx = WuxContext()
    ctx.set_simulation(project, configuration)
    assert not ctx.simulation
    ctx.set_globals(str(target_dir), project, configuration)
    # mf, mh, ips must be initialized
    assert wux.mf
    assert wux.mh
    assert wux.ips

    f = StringIO()
    ctx.gen_contexts_declaration(f, project)
    text = f.getvalue()
    reference = '\n'.join(
        [
            '/* contexts */',
        ]
    )
    assert text.strip('\n') == reference
    f.close()

    f = StringIO()
    ctx.gen_contexts_definition(f)
    text = f.getvalue()
    definitions = set(text.strip('\n').split('\n'))
    assert definitions == {
        '/* contexts */',
    }
    f.close()

    f = StringIO()
    ctx.gen_init(f)
    text = f.getvalue()
    reference = '\n'.join(
        [
            '/* initializations */',
            'void WuxReset()',
            '{',
            '}',
            '',
            'void WuxInit()',
            '{',
            '#   ifndef KCG_USER_DEFINED_INIT',
            '    Node_init_P();',
            '#   else',
            '#   ifndef KCG_NO_EXTERN_CALL_TO_RESET',
            '    Node_reset_P();',
            '#   endif /* KCG_NO_EXTERN_CALL_TO_RESET */',
            '#   endif /* KCG_USER_DEFINED_INIT */',
            '}',
        ]
    )
    assert text.strip('\n') == reference
    f.close()

    f = StringIO()
    ctx.gen_cycles(f)
    text = f.getvalue()
    reference = '\n'.join(
        [
            'void WuxCycle()',
            '{',
            '    Node_P();',
            '}',
        ]
    )
    assert text.strip('\n') == reference
    f.close()

    # extended IP
    ip = wux.ips[0]
    io = ip.get_generated_path('P::Node/origin/')
    assert io == 'origin'
    io = ip.get_generated_path('P::Node/out/')
    assert io == 'out'
    io = ip.get_generated_path('P::speed/')
    assert io == 'speed_P'
    # extended ip, cf. kcgcontext.py
    var = ip.get_in_context_var()  # type: ignore
    assert var == ''
    # extended ip, cf. kcgcontext.py
    var = ip.get_out_context_var()  # type: ignore
    assert var == ''


def test_kcgcontext_generate(tmpdir):
    # make sure the generation does not fail:
    # generated code tested by integration tests
    reset_test_env()
    stub = get_stub()
    path = Path(__file__).parent / 'UT' / 'KcgContext' / 'KcgContext.etp'
    project = load_project(path)
    configuration = project.find_configuration('UT KCG')
    assert configuration
    # remind the target directory to ease its access for manual verifications
    print('tmpdir:', tmpdir)
    # copy the mapping file to the target directory
    shutil.copy(path.parent / configuration.name / 'mapping.xml', tmpdir)
    # exercise the module interface
    ctx_service = ServiceProxy(wux_ctx)
    # make sure init can be called
    dependencies = ctx_service.init(tmpdir, project, configuration)
    assert len(dependencies) > 0

    ctx_service.generate(tmpdir, project, configuration)
    # minimum assessment: generated files
    files = {Path(_).name for _ in stub.generated_files[WuxContext.tool]}
    model = path.stem
    assert files == {'wuxctx%s.c' % model, 'wuxctx%s.h' % model}
