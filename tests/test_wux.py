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

"""Unit tests for wux.py."""

from io import StringIO
from pathlib import Path

import pytest

from ansys.scade.wux.test.sctoc_stub import reset_stub
import ansys.scade.wux.wux as wux
from conftest import load_project, load_sdy_application, load_session


def test_add_sources():
    stub = reset_stub()
    assert stub.c_files == {}
    wux.reset()
    wux.add_sources([Path('a.c'), Path('b.c')])
    wux.add_sources([])
    wux.add_sources([Path('b.c'), Path('d.cpp')])
    assert set(stub.c_files['WUX']) == {
        ('a.c', False),
        ('b.c', False),
        ('d.cpp', False),
    }


def test_add_includes():
    stub = reset_stub()
    assert stub.includes == []
    wux.reset()
    wux.add_includes([Path('a/c'), Path('b')])
    wux.add_includes([])
    wux.add_includes([Path('b'), Path('d/cpp')])
    assert set(stub.includes) == {
        ('a/c', False),
        ('b', False),
        ('d/cpp', False),
    }


def test_add_libraries():
    stub = reset_stub()
    assert stub.obj_files == []
    wux.reset()
    wux.add_libraries([Path('a.o'), Path('b.obj')])
    wux.add_libraries([Path('lib/c.a')])
    wux.add_libraries([Path('a.o'), Path('d.lib')])
    assert set(stub.obj_files) == {
        ('a.o', False),
        ('b.obj', False),
        ('lib/c.a', False),
        ('d.lib', False),
    }


def test_add_definitions():
    stub = reset_stub()
    assert stub.preprocessor_definitions == []
    wux.reset()
    wux.add_definitions('A', 'B')
    wux.add_definitions()
    wux.add_definitions('B', 'C')
    assert set(stub.preprocessor_definitions) == {'A', 'B', 'C'}


@pytest.mark.parametrize(
    'tabs, text, expected',
    [
        (0, '', '\n'),
        (1, '', '    \n'),
        (2, 'a\nb', '        a\nb\n'),
        (1, 'hello', '    hello\n'),
    ],
)
def test_writeln(tabs, text, expected):
    f = StringIO()
    wux.writeln(f, tabs, text)
    result = f.getvalue()
    assert result == expected
    f.close()


@pytest.mark.parametrize(
    'tabs, text, expected',
    [
        (0, '', ''),
        (1, '', ''),
        (2, 'a\nb\n', '        a\n        b\n'),
        (1, 'hello', '    hello\n'),
    ],
)
def test_write_indent(tabs, text, expected):
    f = StringIO()
    wux.write_indent(f, '    ' * tabs, text)
    result = f.getvalue()
    assert result == expected
    f.close()


def test_gen_start_protect():
    f = StringIO()
    wux.gen_start_protect(f, 'MyFile.h')
    result = f.getvalue()
    assert result.strip('\n') == '\n'.join(
        [
            '#ifndef _MYFILE_H_',
            '#define _MYFILE_H_',
        ]
    )
    f.close()


def test_gen_end_protect():
    f = StringIO()
    wux.gen_end_protect(f, 'MyFile.h')
    result = f.getvalue()
    assert result.strip('\n') == '#endif /* _MYFILE_H_ */'
    f.close()


def test_gen_header():
    f = StringIO()
    wux.gen_header(f, 'great tool')
    result = f.getvalue()
    assert result.strip('\n') == '/* generated by great tool */'
    f.close()

    f = StringIO()
    wux.gen_header(f, 'another one', '# ', '')
    result = f.getvalue()
    assert result.strip('\n') == '# generated by another one'
    f.close()

    f = StringIO()
    wux.gen_header(f, 'last one', '<!-- ', ' -->')
    result = f.getvalue()
    assert result.strip('\n') == '<!-- generated by last one -->'
    f.close()


def test_gen_footer():
    f = StringIO()
    wux.gen_footer(f)
    result = f.getvalue()
    assert result.strip('\n') == '/* end of file */'
    f.close()

    f = StringIO()
    wux.gen_footer(f, '# ', '')
    result = f.getvalue()
    assert result.strip('\n') == '# end of file'
    f.close()

    f = StringIO()
    wux.gen_footer(f, '<!-- ', ' -->')
    result = f.getvalue()
    assert result.strip('\n') == '<!-- end of file -->'
    f.close()


def test_gen_includes():
    f = StringIO()
    wux.gen_includes(f, ['a.h', 'b.hpp'])
    text = f.getvalue()
    includes = {_.strip() for _ in text.strip(' \n').split('\n') if _.strip()[:2] != '/*'}
    assert includes == {
        '#include "a.h"',
        '#include "b.hpp"',
    }
    f.close()


def test_set_get_models():
    wux.reset()
    # calls to get_roots does nothing
    assert not wux.get_sessions()
    assert not wux.get_sdy_applications()

    path = Path(__file__).parent / 'Variables' / 'Variables.etp'

    session = load_session(path)
    wux.set_sessions([session])
    sessions = wux.get_sessions()
    assert len(sessions) == 1
    assert sessions[0] == session

    mapping = Path(__file__).parent / 'Variables' / 'Variables.sdy'
    display = Path(__file__).parent / 'Variables' / 'Displays' / 'Displays.etp'
    app = load_sdy_application(mapping, session.model, display)
    wux.set_sdy_applications([app])
    apps = wux.get_sdy_applications()
    assert len(apps) == 1
    assert apps[0] == app

    # verify the specifications, once the SCADE Display mapping application is loaded
    project = load_project(path)
    configuration = project.find_configuration('SdyExt')
    assert configuration
    specs = wux.get_specifications(project, configuration)
    # alphabetical order
    names = [Path(_.pathname).stem for _ in specs]
    assert names == ['Speed', 'Throttles']
