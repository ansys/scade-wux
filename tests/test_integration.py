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

import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

import ansys.scade.apitools.info as info
from conftest import diff_files, run

_test_dir = Path(__file__).parent
_path_ut_extention = _test_dir / 'UTExtension'


@pytest.fixture(scope='session')
def wux_ut_ext() -> bool:
    """Install the test package."""
    path = _path_ut_extention / 'Extension'
    cmd = [sys.executable, '-m', 'pip', 'install', '--editable', str(path)]
    status = run(cmd)
    return status.returncode == 0


def _run_scade(*args) -> subprocess.CompletedProcess:
    """Run scade.exe in a subprocess."""
    if not os.environ.get('VIRTUAL_ENV'):
        venv = Path(sys.executable).parent.parent.as_posix()
        print('setting VIRTUAL_ENV to', venv)
        env = os.environ.copy()
        env['VIRTUAL_ENV'] = venv
    else:
        print('using VIRTUAL_ENV =', os.environ.get('VIRTUAL_ENV'))
        env = None
    cmd = [str(info.get_scade_home() / 'SCADE' / 'bin' / 'scade.exe')]
    cmd.extend([str(_) for _ in args])
    status = run(cmd, env)
    return status


def test_generic_integration(wux_ut_ext, tmpdir):
    """Build and execute the model with the unit test extension."""
    assert wux_ut_ext
    # tmpdir: replace LocalPath by Path
    tmpdir = Path(tmpdir)
    if sys.version_info.major != 3 or sys.version_info.minor < 12:
        print(f'test skipped: requires at least Python 3.12 (current: {sys.version})')
        return
    # copy the model
    print('copying model to', tmpdir)
    for file in ['Model.etp', 'P.xscade']:
        shutil.copyfile(_path_ut_extention / 'Model' / file, tmpdir / file)
    integration_dir = tmpdir / 'Integration'
    model = tmpdir / 'Model.etp'
    status = _run_scade('-code', model, '-conf', 'Integration', '-sim')
    assert status.returncode == 0
    cmd = [integration_dir / 'P__Root.exe', '-max_steps', '2', '-max_log', '1']
    status = run(cmd)
    ref = _test_dir / 'ref' / 'wux_ut_ext_stdout.txt'
    res = integration_dir / ref.name
    res.write_text(status.stdout.decode('utf-8').replace('\r', ''))
    assert not diff_files(res, ref)
