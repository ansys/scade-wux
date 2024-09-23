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

"""Unit tests for kcgcontext.py."""

from pathlib import Path
import shutil

import pytest
from sctoc_stub import reset_stub

from ansys.scade.wux.impl.kcgcontext import WuxContext, get_services
import ansys.scade.wux.wux as wux
from conftest import load_project


@pytest.mark.parametrize(
    'p, c, r',
    [
        (['Two', 'UA', 'Two.etp'], 'UT Nominal', {'Two'}),
        (['UTExtension', 'Model', 'Model.etp'], 'UT Nominal', {'Root'}),
        (['Variables', 'Variables.etp'], 'UT Nominal', {'Engine'}),
    ],
)
def test_kcgcontext_nominal(p, c, r, tmpdir):
    stub = reset_stub()

    path = Path(__file__).parent.joinpath(*p)
    project = load_project(path)
    for configuration in project.configurations:
        if configuration.name == c:
            break
    else:
        assert False
    # copy the mapping file to the target directory
    print('tmpdir:', tmpdir)
    shutil.copy(path.parent / c / 'mapping.xml', tmpdir)
    service = get_services()[0]
    # sanity check
    assert service[0] == 'WUX2_CTX'
    for t in service[1:]:
        if t[0] == '-OnGenerate':
            gen = t[1]
            break
    else:
        assert False
    gen(tmpdir, project, configuration)
    # minimum assessments:
    # - generated files
    files = {Path(_).name for _ in stub.generated_files[WuxContext.tool]}
    model = path.stem
    assert files == {'wuxctx%s.c' % model, 'wuxctx%s.h' % model}
    # - root operators
    roots = {_.get_operator().get_name() for _ in wux.ips}
    assert roots == r
