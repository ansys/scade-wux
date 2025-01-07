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

"""Extension for reusable SCADE-Suite co-simulation wrapper."""

from io import TextIOBase
import os
from pathlib import Path
import re
from typing import List, Optional

import scade.code.suite.sctoc as sctoc
from scade.model.project.stdproject import Project
import scade.model.suite as suite
import scade.model.suite.displaycoupling as sdy

from ansys.scade.apitools.query import is_scalar
from ansys.scade.wux import __version__
import ansys.scade.wux.wux as wux
from ansys.scade.wux.wux import writeln

# ----------------------------------------------------------------------------
# wrapper interface: class and methods
# ----------------------------------------------------------------------------


class SdyExt:
    """Generation service for graphical panels (``WUX2_SDY``)."""

    ID = 'WUX2_SDY'
    tool = 'SCADE Suite-Display Extension'
    banner = '%s (WUX %s)' % (tool, __version__)

    script_path = Path(__file__)
    script_dir = script_path.parent

    def __init__(self):
        self.map_file_dir: str = ''
        self.mapping_operators: List[suite.Operator] = []
        self.specifications: List[sdy.Specification] = []
        # files
        self.sources = []

    @classmethod
    def get_service(cls):
        """Declare the generation service SCADE Suite-Display Extension."""
        cls.instance = SdyExt()
        return (cls.ID, ('-OnInit', cls.instance.init), ('-OnGenerate', cls.instance.generate))

    def init(self, target_dir, project, configuration):
        """Initialize the generation service."""
        return [
            ('Code Generator', ('-Order', 'Before')),
            ('WUX2_SDY_PROXY', ('-Order', 'Before')),
            ('WUX2_CTX', ('-Order', 'Before')),
        ]

    def generate(self, target_dir, project, configuration):
        """Generate the files."""
        print(self.banner)

        assert wux.mf
        roots = wux.mf.get_root_operators()
        self.specifications = wux.get_specifications(project, configuration)

        sdy_application = wux.get_sdy_applications()[0]
        for root in roots:
            if not sdy_application.mapping_file:
                continue
            for op in sdy_application.mapping_file.mapping_operators:
                if (op.name + '/') == root.get_scade_path():
                    self.mapping_operators.append(op)
                    break
            else:
                self.mapping_operators.append(None)

        # generation
        self.generate_display(target_dir, project, configuration, roots, wux.ips)

        # build
        self.declare_target(target_dir, project, configuration, roots)

        return True

    # ----------------------------------------------------------------------------
    # wrapper implementation
    # ----------------------------------------------------------------------------

    def generate_display(self, target_dir, project, configuration, roots, ips):
        """Generate the file for a graphical panel."""
        path = Path(project.pathname)
        pathname = Path(target_dir) / ('wuxsdy' + path.stem + '.c')
        sctoc.add_generated_files(self.tool, [pathname.name])
        self.sources.append(pathname)
        with open(str(pathname), 'w') as f:
            wux.gen_header(f, self.banner)
            self.gen_includes(f, project)
            self.gen_init(f)
            self.gen_draw(f)
            self.gen_ios(f, ips)
            self.gen_cancelled(f)
            wux.gen_footer(f)

    # Find spec by basename
    def get_spec_from_basename(self, basename: str) -> Optional[sdy.Specification]:
        """Get the specification instance for a file."""
        for spec in self.specifications:
            if os.path.abspath(spec.pathname) == os.path.abspath(
                os.path.join(self.map_file_dir, basename)
            ):
                return spec
        return None

    # ----------------------------------------------------------------------------
    # generation
    # ----------------------------------------------------------------------------

    def declare_local_vars(
        self,
        f: TextIOBase,
        scs_class,
        scs_subelement,
        local_var_name,
        sdy_class,
        sdy_type,
        sdy_prefix,
    ):
        """Generate the declaration of the local variables."""
        # Resolve class types
        while isinstance(sdy_class, suite.NamedType) and not sdy_class.is_predefined():
            sdy_class = sdy_class.type
        while isinstance(scs_class, suite.NamedType) and not scs_class.is_predefined():
            scs_class = scs_class.type
        if scs_class.is_generic():
            print_error('Type of {} cannot be generic.'.format(local_var_name))
        # Array case
        elif isinstance(scs_class, suite.Table):
            if scs_subelement == '':
                while sdy_class and isinstance(sdy_class.owner, suite.NamedType):
                    sdy_class = sdy_class.owner
                if sdy_class and isinstance(sdy_class, suite.NamedType):
                    writeln(f, 2, '{}{} {};'.format(sdy_prefix, sdy_class.name, local_var_name))
                else:
                    local_var_name2 = '{}[{}]'.format(local_var_name, scs_class.size)
                    self.declare_local_vars(
                        f,
                        scs_class.type,
                        scs_subelement,
                        local_var_name2,
                        sdy_class.type,
                        sdy_type,
                        sdy_prefix,
                    )
            else:
                match = re.match(r'^\[\d+\](.*)$', scs_subelement)
                if match:
                    scs_subelement2 = match.groups()[0]
                    self.declare_local_vars(
                        f,
                        scs_class.type,
                        scs_subelement2,
                        local_var_name,
                        sdy_class,
                        sdy_type,
                        sdy_prefix,
                    )
                else:
                    print_error(
                        'Invalid element access {} for {}.'.format(scs_subelement, local_var_name)
                    )
        # Structure case
        elif isinstance(scs_class, suite.Structure):
            if scs_subelement == '':
                while sdy_class and isinstance(sdy_class.owner, suite.NamedType):
                    sdy_class = sdy_class.owner
                if sdy_class and isinstance(sdy_class, suite.NamedType):
                    writeln(f, 2, '{}{} {};'.format(sdy_prefix, sdy_class.name, local_var_name))
                else:
                    # "name : type" => "@type@ name"
                    sdy_type = re.sub(
                        r'([a-zA-Z_]+[a-zA-Z_0-9]*) : ([a-zA-Z_]+[a-zA-Z_0-9]*)',
                        r'@\2@ \1',
                        sdy_type,
                    )
                    # "^DDD" => "[DDD]"
                    sdy_type = re.sub(r' \^([a-zA-Z_0-9]+)', r'\[\1\]', sdy_type)
                    #  => display-type
                    sdy_type = re.sub(r'@bool@', r'SGLbool', sdy_type)
                    sdy_type = re.sub(r'@char@', r'SGLbyte', sdy_type)
                    sdy_type = re.sub(r'@int@', r'SGLlong', sdy_type)
                    sdy_type = re.sub(r'@real@', r'SGLfloat', sdy_type)
                    sdy_type = re.sub(r'@float32@', r'SGLfloat', sdy_type)
                    sdy_type = re.sub(r'@float64@', r'SGLdouble', sdy_type)
                    sdy_type = re.sub(r'@(u?int\d+)@', r'SGL\1', sdy_type)
                    # finish
                    sdy_type = re.sub(r'@([a-zA-Z_0-9]+)@', sdy_prefix + r'\1', sdy_type)
                    sdy_type = re.sub(r',', ';', sdy_type)
                    sdy_type = re.sub(r'}', ';}', sdy_type)
                    writeln(f, 2, 'struct {} {};'.format(sdy_type, local_var_name))
            else:
                match = re.search(r'^\.([^\.\[]+)(.*)$', scs_subelement)
                if match:
                    idx = match.group(1)
                    scs_subelement2 = match.group(2)
                    for field in scs_class.elements:
                        if field.name == idx:
                            self.declare_local_vars(
                                f,
                                field.type,
                                scs_subelement2,
                                local_var_name,
                                sdy_class,
                                sdy_type,
                                sdy_prefix,
                            )
                            break
                    else:
                        print_error('Invalid element access {} for {}.'.format(idx, local_var_name))
                else:
                    print_error(
                        'Invalid element access {} for {}.'.format(scs_subelement, local_var_name)
                    )
        # Scalar case
        elif isinstance(scs_class, suite.Enumeration):
            writeln(f, 2, 'SGLlong {};'.format(local_var_name))
        elif re.match(r'^bool|char|int|real|float32|float64|u?int[0-9]+$', scs_class.name):
            #  => display-type
            sdy_type = re.sub(r'^bool$', r'SGLbool', scs_class.name)
            sdy_type = re.sub(r'^char$', r'SGLbyte', sdy_type)
            sdy_type = re.sub(r'^int$', r'SGLlong', sdy_type)
            sdy_type = re.sub(r'^real$', r'SGLfloat', sdy_type)
            sdy_type = re.sub(r'^float32$', r'SGLfloat', sdy_type)
            sdy_type = re.sub(r'^float64$', r'SGLdouble', sdy_type)
            sdy_type = re.sub(r'^(u?int\d+)$', r'SGL\1', sdy_type)
            writeln(f, 2, '{} {};'.format(sdy_type, local_var_name))
        else:
            print_error('Type {} of {} is unknown.'.format(scs_class.name, local_var_name))

    def fix_indexes(self, subelements):
        """Adjust the indexes."""
        # Subtract 1 to indexes (in connection file, indexing starts at 1)
        return re.sub(r'\[(\d+)\]', lambda m: '[{}]'.format(int(m.group(1)) - 1), subelements)

    def convert_var(
        self,
        f: TextIOBase,
        kind,
        level,
        scs_class,
        scs_subelement,
        local_var_name,
        cpath,
        sdy_class,
        pluggable,
    ):
        """Generate the assignments."""
        # Resolve class types
        while isinstance(sdy_class, suite.NamedType) and not sdy_class.is_predefined():
            sdy_class = sdy_class.type
        while isinstance(scs_class, suite.NamedType) and not scs_class.is_predefined():
            scs_class = scs_class.type
        if scs_class.is_generic():
            print_error('Type of {} cannot be generic.'.format(local_var_name))
        # Array case
        elif isinstance(scs_class, suite.Table):
            if scs_subelement == '':
                idx = 'i' + str(level)
                writeln(f, level + 1, 'int {idx};'.format(idx=idx))
                writeln(
                    f,
                    level + 1,
                    'for ({idx} = 0; {idx} < {size}; {idx}++) {{'.format(
                        idx=idx, size=scs_class.size
                    ),
                )
                local_var_name2 = '{}[{}]'.format(local_var_name, idx)
                cpath2 = '{}[{}]'.format(cpath, idx)
                self.convert_var(
                    f,
                    kind,
                    level + 1,
                    scs_class.type,
                    scs_subelement,
                    local_var_name2,
                    cpath2,
                    sdy_class.type,
                    pluggable,
                )
                writeln(f, level + 1, '}')
            else:
                match = re.match(r'^\[\d+\](.*)$', scs_subelement)
                if match:
                    scs_subelement2 = match.groups()[0]
                    self.convert_var(
                        f,
                        kind,
                        level,
                        scs_class.type,
                        scs_subelement2,
                        local_var_name,
                        cpath,
                        sdy_class,
                        pluggable,
                    )
                else:
                    print_error(
                        'Invalid element access {} for {}.'.format(scs_subelement, local_var_name)
                    )
        # Structure case
        elif isinstance(scs_class, suite.Structure):
            if scs_subelement == '':
                scs_fields = []
                sdy_fields = []
                for elem in scs_class.elements:
                    scs_fields.append(elem)
                if sdy_class and isinstance(sdy_class, suite.Structure):
                    for elem in sdy_class.elements:
                        sdy_fields.append(elem)
                else:
                    for elem in pluggable.pluggables:
                        sdy_fields.append(elem)
                for fs, fd in zip(scs_fields, sdy_fields):
                    local_var_name2 = '{}.{}'.format(local_var_name, fd.name)
                    cpath2 = '{}.{}'.format(cpath, fs.name)
                    self.convert_var(
                        f,
                        kind,
                        level,
                        fs.type,
                        scs_subelement,
                        local_var_name2,
                        cpath2,
                        fd.type,
                        pluggable,
                    )
            else:
                match = re.search(r'^\.([^\.\[]+)(.*)$', scs_subelement)
                if match:
                    idx = match.group(1)
                    scs_subelement2 = match.group(2)
                    for field in scs_class.elements:
                        if field.name == idx:
                            self.convert_var(
                                f,
                                kind,
                                level,
                                field.type,
                                scs_subelement2,
                                local_var_name,
                                cpath,
                                sdy_class,
                                pluggable,
                            )
                            break
                    else:
                        print_error('Invalid element access {} for {}.'.format(idx, local_var_name))
                else:
                    print_error(
                        'Invalid element access {} for {}.'.format(scs_subelement, local_var_name)
                    )
        # Scalar case
        else:
            if kind == 'output':
                writeln(f, level + 1, '{} = {};'.format(local_var_name, cpath))
            else:
                writeln(f, level + 1, '{} = {};'.format(cpath, local_var_name))

    def gen_suite_display_connection(self, f: TextIOBase, ip, output, input):
        """Generate the Suite to Display connections."""
        # Compute SCADE Suite output characteristics
        output_instance_path = output.instancepath
        if output_instance_path == '':
            # The variable is not a probe, get the path of the operator owning the Scade variable
            output_instance_path = output.variable.owner.get_full_path()
        output_subelement = self.fix_indexes(output.subelement)
        output_c = ip.get_generated_path(output_instance_path + output.name + output_subelement)
        # Compute SCADE Display input characteristics
        input_spec = self.get_spec_from_basename(input.pathname)
        input_subelement = self.fix_indexes(input.subelement)
        if input_spec and output_c:
            # Compute Display input variable access
            if input.object_type:
                if input_subelement == '':
                    input_c = '{}_{}_S_{}({}_L_{}()'.format(
                        input_spec.prefix, input.layer, input.name, input_spec.prefix, input.layer
                    )
                else:
                    input_c = 'kcg_assign(&{}_{}_G_{}({}_L_{}()){}'.format(
                        input_spec.prefix,
                        input.layer,
                        input.name,
                        input_spec.prefix,
                        input.layer,
                        input_subelement,
                    )
            else:
                field = re.search(r'([a-zA-Z_]+[a-zA-Z_0-9]*) : .*', input.type).group(1)
                input_c = 'kcg_assign(&{}_L_{}()->{}'.format(input_spec.prefix, input.layer, field)
            # Call Display input setter macro, arrays and structures are passed as pointers
            writeln(
                f,
                1,
                '/* {}{} => {}{} */'.format(
                    output.name, output_subelement, input.name, input_subelement
                ),
            )
            if is_scalar(output.variable.type):
                if not input_subelement:
                    writeln(f, 1, '{}, {});'.format(input_c, output_c))
                else:
                    writeln(f, 1, '{0}, &{1}, sizeof({1}));'.format(input_c, output_c))
            else:
                # Perform conversion
                local_var_name = 'v'
                writeln(f, 1, '{')
                self.declare_local_vars(
                    f,
                    output.variable.type,
                    output_subelement,
                    local_var_name,
                    input.object_type,
                    input.type,
                    input_spec.prefix + '_',
                )
                # project anonymous compound types
                if re.fullmatch(r'{.*}', input.type):
                    local_var_name = local_var_name + input_subelement
                self.convert_var(
                    f,
                    'output',
                    1,
                    output.variable.type,
                    output_subelement,
                    local_var_name,
                    output_c,
                    input.object_type,
                    input.pluggable,
                )
                if input.object_type:
                    if not input_subelement:
                        writeln(f, 2, '{}, {});'.format(input_c, local_var_name))
                    else:
                        writeln(f, 2, '{0}, &{1}, sizeof({1}));'.format(input_c, local_var_name))
                else:
                    writeln(f, 2, '{0}, &{1}, sizeof({1}));'.format(input_c, local_var_name))
                writeln(f, 1, '}')
        else:
            if output_c:
                # Correct connection, but disabled in this configuration
                print_info(
                    'Skipping connection {}{} => {}{}.'.format(
                        output.name, output_subelement, input.name, input_subelement
                    )
                )
            else:
                # Bad connection
                print_info(
                    'Invalid connection {}{} => {}{}. Please update the connections!'.format(
                        output.name, output_subelement, input.name, input_subelement
                    )
                )

    def gen_display_suite_connection(self, f: TextIOBase, ip, output, input):
        """Generate the Display to Suite connections."""
        # Compute SCADE Suite input characteristics
        input_instance_path = input.instancepath
        if input_instance_path == '':
            # The variable is not a probe, get the path of the operator owning the Scade variable
            input_instance_path = input.variable.owner.get_full_path()
        intput_subelement = self.fix_indexes(input.subelement)
        input_c = ip.get_generated_path(input_instance_path + input.name + intput_subelement)
        # Compute SCADE Display output characteristics
        output_spec = self.get_spec_from_basename(output.pathname)
        output_subelement = self.fix_indexes(output.subelement)
        if output_spec and input_c:
            # Call Display output getter macro
            writeln(
                f,
                1,
                '/* {}{} <= {}{} */'.format(
                    input.name, intput_subelement, output.name, output_subelement
                ),
            )
            writeln(f, 1, '{')
            if output.object_type:
                output_c = '{}_{}_G_{}({}_L_{}())'.format(
                    output_spec.prefix, output.layer, output.name, output_spec.prefix, output.layer
                )
                # Perform conversion
                local_var_name = 'v'
                self.declare_local_vars(
                    f,
                    input.variable.type,
                    intput_subelement,
                    local_var_name,
                    output.object_type,
                    output.type,
                    output_spec.prefix + '_',
                )
                # project anonymous compound types
                if re.fullmatch(r'{.*}', input.type_definition):
                    writeln(
                        f,
                        2,
                        'kcg_assign(&{}, &({}){}, sizeof({}));'.format(
                            local_var_name, output_c, output_subelement, local_var_name
                        ),
                    )
                elif re.fullmatch(r'.*\^.*', input.type_definition):
                    writeln(
                        f,
                        2,
                        'kcg_assign({}, ({}){}, sizeof({}));'.format(
                            local_var_name, output_c, output_subelement, local_var_name
                        ),
                    )
                else:
                    writeln(f, 2, '{} = {}{};'.format(local_var_name, output_c, output_subelement))
                self.convert_var(
                    f,
                    'input',
                    1,
                    input.variable.type,
                    intput_subelement,
                    local_var_name,
                    input_c,
                    output.object_type,
                    output.pluggable,
                )
            else:
                # must be a group
                scs_class = input.object_type
                while isinstance(scs_class, suite.NamedType) and not scs_class.is_predefined():
                    scs_class = scs_class.type
                scs_fields = []
                for elem in scs_class.elements:
                    scs_fields.append(elem)
                sdy_fields = []
                for elem in output.pluggable.pluggables:
                    sdy_fields.append(elem)
                i = 0
                for fs, fd in zip(scs_fields, sdy_fields):
                    i += 1
                    local_var_name = 'v' + str(i)
                    self.declare_local_vars(
                        f,
                        fs.type,
                        '',
                        local_var_name,
                        fd.type,
                        output.type,
                        output_spec.prefix + '_',
                    )
                    ouput_c = '{}_{}_G_{}({}_L_{}())'.format(
                        output_spec.prefix, output.layer, fd.name, output_spec.prefix, output.layer
                    )
                    field_class = fs.type
                    while (
                        isinstance(field_class, suite.NamedType) and not field_class.is_predefined()
                    ):
                        field_class = field_class.type
                    if isinstance(field_class, suite.Structure):
                        writeln(
                            f,
                            2,
                            'kcg_assign(&{}, &{}, sizeof({}));'.format(
                                local_var_name, ouput_c, local_var_name
                            ),
                        )
                    elif isinstance(field_class, suite.Table):
                        writeln(
                            f,
                            2,
                            'kcg_assign({}, &{}, sizeof({}));'.format(
                                local_var_name, ouput_c, local_var_name
                            ),
                        )
                    else:
                        writeln(f, 2, '{} = {};'.format(local_var_name, ouput_c))
                    input_c2 = '{}.{}'.format(input_c, fs.name)
                    self.convert_var(
                        f,
                        'input',
                        1,
                        fs.type,
                        '',
                        local_var_name,
                        input_c2,
                        fd.type,
                        output.pluggable,
                    )
            writeln(f, 1, '}')
        else:
            if input_c:
                # Correct connection, but disabled in this configuration
                print_info(
                    'Skipping connection {}{} <= {}{}.'.format(
                        input.name, intput_subelement, output.name, output_subelement
                    )
                )
            else:
                # Bad connection
                print_info(
                    'Invalid connection {}{} <= {}{}. Please update the connections!'.format(
                        input.name, intput_subelement, output.name, output_subelement
                    )
                )

    def gen_includes(self, f: TextIOBase, project: Project):
        """Generate the include directives."""
        writeln(f, 0, '/* SCADE Suite contexts */')
        writeln(f, 0, '#include "wuxctx%s.h"' % Path(project.pathname).stem)
        writeln(f)
        writeln(f, 0, '/* SCADE Display includes */')
        writeln(f, 0, '#include <malloc.h>')
        if len(self.specifications):
            writeln(f, 0, '#include "sdy/sdy_events.h"')
            for spec in self.specifications:
                writeln(f, 0, '#include "sdy/{}.h"'.format(spec.prefix))
        writeln(f)
        writeln(f, 0, '#include "WuxSdyExt.h"')
        writeln(f)

    def gen_init(self, f: TextIOBase):
        """Generate the initialization calls."""
        count = len(self.specifications)
        writeln(f, 0, '/* SCADE Display init */')
        writeln(f, 0, '#ifdef WUX_DISPLAY_AS_BUFFERS')
        writeln(f, 0, 'static WuxSdyScreen _screens[%d];' % count)
        writeln(f, 0, '')
        writeln(f, 0, 'int WuxSdyGetScreenCount()')
        writeln(f, 0, '{')
        writeln(f, 1, 'return %d;' % count)
        writeln(f, 0, '}')
        writeln(f, 0, '')
        writeln(f, 0, 'const WuxSdyScreen* WuxSdyGetScreen(int index)')
        writeln(f, 0, '{')
        writeln(f, 1, 'return index >= 0 && index < %d ? &_screens[index] : NULL;' % count)
        writeln(f, 0, '}')
        writeln(f, 0, '')
        writeln(f, 0, 'void WuxSdyInit()')
        writeln(f, 0, '{')
        for i, spec in enumerate(self.specifications):
            writeln(f, 1, '/* Init of {} */'.format(spec.prefix))
            writeln(f, 1, '_screens[%d].name = "%s";' % (i, Path(spec.pathname).stem))
            writeln(f, 1, '_screens[%d].width = %s__screen_width();' % (i, spec.prefix))
            writeln(f, 1, '_screens[%d].height = %s__screen_height();' % (i, spec.prefix))
            writeln(f, 1, '_screens[%d].buffer = %s__init_buffer();' % (i, spec.prefix))
            writeln(
                f,
                1,
                '_screens[{0}].size = _screens[{0}].width * _screens[{0}].height * 4;'.format(i),
            )
        writeln(f, 0, '}')
        writeln(f, 0, '#else')
        writeln(f, 0, 'void WuxSdyInit()')
        writeln(f, 0, '{')
        for spec in self.specifications:
            writeln(f, 1, '/* Init of {} */'.format(spec.prefix))
            writeln(f, 1, '{}__init();'.format(spec.prefix))
        writeln(f, 0, '}')
        writeln(f, 0, '#endif /* WUX_DISPLAY_AS_BUFFERS */')
        writeln(f)

    def gen_draw(self, f: TextIOBase):
        """Generate the calls to the drawing functions."""
        writeln(f, 0, '/* SCADE Display cycle */')
        writeln(f, 0, 'void WuxSdyDraw()')
        writeln(f, 0, '{')
        for spec in self.specifications:
            writeln(f, 1, '/* Draw of {} */'.format(spec.prefix))
            writeln(f, 1, '{}__draw();'.format(spec.prefix))
        writeln(f, 0, '}')
        writeln(f)

    def gen_ios(self, f: TextIOBase, ips):
        """Generate the calls to connection functions."""
        writeln(f, 0, '/* Connections Suite => Display */')
        writeln(f, 0, 'void WuxSdySetInputs()')
        writeln(f, 0, '{')
        if self.specifications:
            for spec in self.specifications:
                writeln(f, 1, '{}__lockio();'.format(spec.prefix))
            for op, ip in zip(self.mapping_operators, ips):
                if op:
                    for item in op.mapping_items:
                        if isinstance(item.sender, sdy.MappingVariable):
                            for input in item.receivers:
                                if isinstance(input, sdy.MappingPlug):
                                    self.gen_suite_display_connection(f, ip, item.sender, input)
            for spec in self.specifications:
                writeln(f, 1, '{}__unlockio();'.format(spec.prefix))
        writeln(f, 0, '}')
        writeln(f)
        writeln(f, 0, '/* Connections Suite <= Display */')
        writeln(f, 0, 'void WuxSdyGetOutputs()')
        writeln(f, 0, '{')
        if self.specifications:
            for spec in self.specifications:
                writeln(f, 1, '{}__lockio();'.format(spec.prefix))
            for op, ip in zip(self.mapping_operators, ips):
                if op:
                    for item in op.mapping_items:
                        if isinstance(item.sender, sdy.MappingPlug):
                            for input in item.receivers:
                                if isinstance(input, sdy.MappingVariable):
                                    self.gen_display_suite_connection(f, ip, item.sender, input)
            for spec in self.specifications:
                writeln(f, 1, '{}__unlockio();'.format(spec.prefix))
        writeln(f, 0, '}')
        writeln(f)

    def gen_cancelled(self, f: TextIOBase):
        """Generate the call cancel functions."""
        writeln(f, 0, '/* SCADE Display cancelled */')
        writeln(f, 0, 'int WuxSdyCancelled()')
        writeln(f, 0, '{')
        for spec in self.specifications:
            writeln(f, 1, 'if ({}__cancelled()) return 1;'.format(spec.prefix))
        writeln(f, 1, 'return 0;')
        writeln(f, 0, '}')
        writeln(f)

    # ----------------------------------------------------------------------------
    # build
    # ----------------------------------------------------------------------------

    def declare_target(self, target_dir, project, configuration, roots):
        """Update the makefile: sources and include search paths."""
        # runtime files
        include = self.script_dir.parent / 'include'
        wux.add_includes([include])
        wux.add_sources(self.sources)


# ----------------------------------------------------------------------------
# misc.
# ----------------------------------------------------------------------------


def print_info(*messages):
    """Print information messages."""
    print(*messages)


def print_error(message):
    """Print error messages."""
    print('ERROR: ', message)


# ----------------------------------------------------------------------------
# list of services
# ----------------------------------------------------------------------------


def get_services():
    """Return the list of Generation services implemented by this module."""
    return [SdyExt.get_service()]
