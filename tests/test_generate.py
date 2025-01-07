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
import ansys.scade.wux.wux as wux
from conftest import diff_files, load_project, load_sdy_application, load_session


@pytest.mark.parametrize(
    'file, display, name',
    [
        ('UT/KcgContext/KcgContext.etp', None, 'UT KCG'),
        ('Two/UA/Two.etp', 'Two/DF/TwoDF.etp', 'UT KCG'),
        ('Two/UA/Two.etp', 'Two/DF/TwoDF.etp', 'UT Simulation'),
        ('Variables/Variables.etp', 'Variables/Displays/Displays.etp', 'UT KCG'),
        ('Variables/Variables.etp', 'Variables/Displays/Displays.etp', 'UT Simulation'),
        ('Types/Logic/Model.etp', 'Types/Graphics/Types.etp', 'UT KCG'),
    ],
)
def test_generate(file, name, display, tmpdir):
    # make sure the generation does not fail:
    # generated code tested by integration tests
    reset_test_env()
    stub = get_stub()

    test_dir = Path(__file__).parent
    path = test_dir / file
    project = load_project(path)
    configuration = project.find_configuration(name)
    assert configuration
    model = path.stem
    # remind the target directory to ease its access for manual verifications
    print('tmpdir:', tmpdir)
    # copy the mapping file to the target directory
    shutil.copy(path.parent / configuration.name / 'mapping.xml', tmpdir)

    # models
    session = load_session(path)
    wux.set_sessions([session])
    if display:
        mapping = path.with_suffix('.sdy')
        app = load_sdy_application(mapping, session.model, test_dir / display)
    else:
        app = load_sdy_application(None, session.model)
    wux.set_sdy_applications([app])

    # initialize the context, required for all other services
    ctx = ServiceProxy(wux_ctx)
    ctx.init(tmpdir, project, configuration)
    status = ctx.generate(tmpdir, project, configuration)
    assert status

    # generated files
    paths = []

    # WUX2_SDY_PROXY
    proxy = ServiceProxy(wux_proxy)
    proxy.init(tmpdir, project, configuration)
    status = proxy.generate(tmpdir, project, configuration)
    assert status
    # minimum assessment: generated files
    proxy_paths = [Path(tmpdir) / _ for _ in stub.generated_files[wux_proxy.SdyProxyExt.tool]]
    files = {_.name for _ in proxy_paths}
    paths.extend(proxy_paths)
    assert files == {'wuxsdyprx%s.cpp' % model}

    # WUX2_SDY
    sdy = ServiceProxy(wux_sdy)
    sdy.init(tmpdir, project, configuration)
    status = sdy.generate(tmpdir, project, configuration)
    assert status
    # minimum assessment: generated files
    sdy_paths = [Path(tmpdir) / _ for _ in stub.generated_files[wux_sdy.SdyExt.tool]]
    files = {_.name for _ in sdy_paths}
    paths.extend(sdy_paths)
    assert files == {'wuxsdy%s.c' % model}

    # WUX2_UAA
    uaa = ServiceProxy(wux_uaa)
    uaa.init(tmpdir, project, configuration)
    status = uaa.generate(tmpdir, project, configuration)
    assert status
    # minimum assessment: generated files
    uaa_paths = [Path(tmpdir) / _ for _ in stub.generated_files[wux_uaa.A661UAA.tool]]
    files = {_.name for _ in uaa_paths}
    paths.extend(uaa_paths)
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

    # references
    # compare to a reference file if exists
    for p in paths:
        ref = test_dir / 'ref' / ('generate_' + p.stem + '_' + '_'.join(name.split()) + p.suffix)
        if ref.exists():
            failure = diff_files(ref, p)
            assert not failure
