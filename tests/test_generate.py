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

import ansys.scade.wux.impl.a661 as uaa
import ansys.scade.wux.impl.kcgcontext as ctx
import ansys.scade.wux.impl.sdyext as sdy
import ansys.scade.wux.impl.simuext as simu_ext
from ansys.scade.wux.test.sctoc_stub import reset_stub
import ansys.scade.wux.wux as wux
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
    wux.reset()
    ctx.WuxContext.reset()
    stub = reset_stub()

    path = Path(__file__).parent / file
    project = load_project(path)
    configuration = find_configuration(project, name)
    model = path.stem
    # remind the target directory to ease its access for manual verifications
    print('tmpdir:', tmpdir)
    # copy the mapping file to the target directory
    shutil.copy(path.parent / configuration.name / 'mapping.xml', tmpdir)

    # initialize the context, required for all other services
    ctx.WuxContext.init(tmpdir, project, configuration)
    status = ctx.WuxContext.generate(tmpdir, project, configuration)
    assert status

    # WUX2_SDY
    sdy.SdyExt.sources = []  # TODO provide at least a reset function
    sdy.SdyExt.init(tmpdir, project, configuration)
    status = sdy.SdyExt.generate(tmpdir, project, configuration)
    assert status
    # minimum assessment: generated files
    files = {Path(_).name for _ in stub.generated_files[sdy.SdyExt.tool]}
    assert files == {'wuxsdy%s.c' % model, 'wuxsdyprx%s.cpp' % model}

    # WUX2_UAA
    uaa.A661UAA.sources = []  # TODO provide at least a reset function
    uaa.A661UAA.init(tmpdir, project, configuration)
    status = uaa.A661UAA.generate(tmpdir, project, configuration)
    assert status
    # minimum assessment: generated files
    files = {Path(_).name for _ in stub.generated_files[uaa.A661UAA.tool]}
    assert files == {'wuxuaa%s.c' % model}

    # WUX2_SIMU_EXT
    # copy the mapping file to the target directory
    interface = model + '_interface.c'
    try:
        shutil.copy(path.parent / configuration.name / interface, tmpdir)
    except FileNotFoundError:
        pass
    simu_ext.WuxSimuExt.init(tmpdir, project, configuration)
    status = simu_ext.WuxSimuExt.generate(tmpdir, project, configuration)
    assert status
    # minimum assessment: generated files
    assert simu_ext.WuxSimuExt.tool not in stub.generated_files
