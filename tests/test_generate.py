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

"""Exercises the services' ``generate`` procedures."""

from pathlib import Path
import shutil

import pytest

import ansys.scade.wux.impl.a661 as wux_uaa
import ansys.scade.wux.impl.kcgcontext as wux_ctx
import ansys.scade.wux.impl.proxyext as wux_proxy
import ansys.scade.wux.impl.sdyext as wux_sdy
import ansys.scade.wux.impl.simuext as wux_simu_ext
from ansys.scade.wux.test.sctoc_stub import get_stub
from ansys.scade.wux.test.utils import ServiceProxy, reset_test_env
from conftest import find_configuration, load_project


@pytest.mark.parametrize(
    'file, name',
    [
        ('Two/UA/Two.etp', 'UT KCG'),
        ('Two/UA/Two.etp', 'UT Simulation'),
        ('Variables/Variables.etp', 'UT KCG'),
        ('Variables/Variables.etp', 'UT Simulation'),
    ],
)
def test_generate(file, name, tmpdir):
    # make sure the generation does not fail:
    # generated code tested by integration tests
    reset_test_env()
    stub = get_stub()

    path = Path(__file__).parent / file
    project = load_project(path)
    configuration = find_configuration(project, name)
    model = path.stem
    # remind the target directory to ease its access for manual verifications
    print('tmpdir:', tmpdir)
    # copy the mapping file to the target directory
    shutil.copy(path.parent / configuration.name / 'mapping.xml', tmpdir)

    # initialize the context, required for all other services
    ctx = ServiceProxy(wux_ctx)
    ctx.init(tmpdir, project, configuration)
    status = ctx.generate(tmpdir, project, configuration)
    assert status

    # WUX2_SDY_PROYX
    proxy = ServiceProxy(wux_proxy)
    proxy.init(tmpdir, project, configuration)
    status = proxy.generate(tmpdir, project, configuration)
    assert status
    # minimum assessment: generated files
    files = {Path(_).name for _ in stub.generated_files[wux_proxy.SdyProxyExt.tool]}
    assert files == {'wuxsdyprx%s.cpp' % model}

    # WUX2_SDY
    sdy = ServiceProxy(wux_sdy)
    sdy.init(tmpdir, project, configuration)
    status = sdy.generate(tmpdir, project, configuration)
    assert status
    # minimum assessment: generated files
    files = {Path(_).name for _ in stub.generated_files[wux_sdy.SdyExt.tool]}
    assert files == {'wuxsdy%s.c' % model}

    # WUX2_UAA
    uaa = ServiceProxy(wux_uaa)
    uaa.init(tmpdir, project, configuration)
    status = uaa.generate(tmpdir, project, configuration)
    assert status
    # minimum assessment: generated files
    files = {Path(_).name for _ in stub.generated_files[wux_uaa.A661UAA.tool]}
    assert files == {'wuxuaa%s.c' % model}

    # WUX2_SIMU_EXT
    # copy the mapping file to the target directory
    interface = model + '_interface.c'
    try:
        shutil.copy(path.parent / configuration.name / interface, tmpdir)
    except FileNotFoundError:
        pass
    simu_ext = ServiceProxy(wux_simu_ext)
    simu_ext.init(tmpdir, project, configuration)
    status = simu_ext.generate(tmpdir, project, configuration)
    assert status
    # minimum assessment: generated files
    assert wux_simu_ext.WuxSimuExt.tool not in stub.generated_files
