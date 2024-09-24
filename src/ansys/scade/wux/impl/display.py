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

"""Connection with SCADE Display specifications (similar to SdyTarget.tcl)."""

import os
import pathlib
import re
import subprocess
import sys

import scade.code.suite.sctoc as sctoc
import scade.model.suite.displaycoupling as displaycoupling
import scade.model.suite.suite as suite

from ansys.scade.apitools.info import get_scade_home
from ansys.scade.wux.wux import writeln

# ----------------------------------------------------------------------------
# variables
# ----------------------------------------------------------------------------

sdy_display_home = None
sdy_rapidproto_home = None
sdy_appplication = None
sdy_mapping_operator = None
sdy_map_file_dir = None
sdy_specifications = []


# Initialize all script global variables
def set_variables(project, configuration, roots):
    global sdy_display_home
    global sdy_rapidproto_home
    global sdy_appplication
    global sdy_mapping_operators
    global sdy_map_file_dir
    global sdy_specifications

    sdy_display_home = None
    sdy_rapidproto_home = None
    sdy_appplication = None
    sdy_map_file_dir = None
    sdy_mapping_operators = []
    sdy_specifications = []

    if not project:
        return

    ansys_scade_dir = get_scade_home()
    sdy_display_home = str(ansys_scade_dir / 'SCADE Display')
    sdy_rapidproto_home = str(ansys_scade_dir / 'SCADE Test' / 'Rapid Prototyper')

    for app in displaycoupling.get_roots():
        if app.mapping_file:
            rootname1 = os.path.abspath(os.path.splitext(app.mapping_file.pathname)[0])
            rootname2 = os.path.abspath(os.path.splitext(project.pathname)[0])
            if rootname1.lower() == rootname2.lower():
                sdy_appplication = app
                break
    else:
        return

    sdy_map_file_dir = os.path.dirname(sdy_appplication.mapping_file.pathname)

    for root in roots:
        for op in sdy_appplication.mapping_file.mapping_operators:
            if (op.name + '/') == root.get_scade_path():
                sdy_mapping_operators.append(op)
                break
        else:
            sdy_mapping_operators.append(None)

    for panel_params in project.get_tool_prop_def(
        'GENERATOR', 'DISPLAY_ENABLED_PANELS', [], configuration
    ):
        params = panel_params.split(',')
        if len(params) >= 2:
            if params[1] != 'None':
                for spec in sdy_appplication.specifications:
                    if (
                        os.path.abspath(spec.pathname)
                        == os.path.abspath(os.path.join(sdy_map_file_dir, params[0]))
                    ) and (spec.sdy_project.is_display() or spec.sdy_project.is_rapid_proto()):
                        sdy_specifications.append(spec)
                        # Set spec.conf and spec.basename
                        spec.conf = params[1]
                        spec.basename = os.path.splitext(os.path.basename(spec.pathname))[0]
    # Sort specifications by basename
    sdy_specifications = sorted(sdy_specifications, key=lambda x: x.basename)
    # Compute specifications prefix
    id_spec_file = 0
    for spec in sdy_specifications:
        id_spec_file += 1
        # Set spec.prefix
        spec.prefix = 'SDY{}_{}'.format(id_spec_file, re.sub(r'[^A-Za-z0-9_]', '_', spec.basename))


# Find spec by basename
def get_spec_from_basename(basename):
    for spec in sdy_specifications:
        if os.path.abspath(spec.pathname) == os.path.abspath(
            os.path.join(sdy_map_file_dir, basename)
        ):
            return spec
    return None


def is_scalar(sctype):
    if sctype.is_predefined():
        return True
    if isinstance(sctype, suite.Enumeration):
        return True
    if isinstance(sctype, suite.NamedType):
        return is_scalar(sctype.type)
    return False


def get_specifications():
    return sdy_specifications


# ----------------------------------------------------------------------------
# generation
# ----------------------------------------------------------------------------


def print_info(*messages):
    print(*messages)


def print_error(message):
    print('ERROR: ', message)


def declare_local_vars(
    f, scs_class, scs_subelement, local_var_name, sdy_class, sdy_type, sdy_prefix
):
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
                declare_local_vars(
                    f,
                    scs_class.type,
                    scs_subelement,
                    local_var_name2,
                    sdy_class.type,
                    sdy_type,
                    sdy_prefix,
                )
        else:
            scs_subelement2 = re.sub(r'^\[\d+\](.*)$', r'\1', scs_subelement)
            if scs_subelement2:
                declare_local_vars(
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
                    r'([a-zA-Z_]+[a-zA-Z_0-9]*) : ([a-zA-Z_]+[a-zA-Z_0-9]*)', r'@\2@ \1', sdy_type
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
                sdy_type = re.sub(r'@([a-zA-Z_0-9]+)@', sdy_prefix + '\1')
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
                        declare_local_vars(
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


def fix_indexes(subelements):
    # Subtract 1 to indexes (in connection file, indexing starts at 1)
    return re.sub(r'\[(\d+)\]', lambda m: '[{}]'.format(int(m.group(1)) - 1), subelements)


def convert_var(
    f, kind, level, scs_class, scs_subelement, local_var_name, cpath, sdy_class, pluggable
):
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
                'for ({idx} = 0; {idx} < {size}; {idx}++) {{'.format(idx=idx, size=scs_class.size),
            )
            local_var_name2 = '{}[{}]'.format(local_var_name, idx)
            cpath2 = '{}[{}]'.format(cpath, idx)
            convert_var(
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
            scs_subelement2 = re.sub(r'^\[\d+\](.*)$', r'\1', scs_subelement)
            if scs_subelement2:
                convert_var(
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
                convert_var(
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
                        convert_var(
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


def gen_suite_display_connection(f, ip, output, input):
    # Compute SCADE Suite output characteristics
    output_instance_path = output.instancepath
    if output_instance_path == '':
        # The variable is not a probe, get the path of the operator owning the Scade variable
        output_instance_path = output.variable.owner.get_full_path()
    output_subelement = fix_indexes(output.subelement)
    output_c = ip.get_generated_path(output_instance_path + output.name + output_subelement)
    # Compute SCADE Display input characteristics
    input_spec = get_spec_from_basename(input.pathname)
    input_subelement = fix_indexes(input.subelement)
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
                writeln(f, 1, '{}, &{}, sizeof({}));'.format(input_c, output_c, output_c))
        else:
            # Perform conversion
            local_var_name = 'v'
            writeln(f, 1, '{')
            declare_local_vars(
                f,
                output.variable.type,
                output_subelement,
                local_var_name,
                input.object_type,
                input.type,
                input_spec.prefix + '_',
            )
            # project anonymous compound types
            if re.match(r'{.*}', input.type):
                local_var_name = local_var_name + input_subelement
            convert_var(
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
                    writeln(
                        f,
                        2,
                        '{}, &{}, sizeof({}));'.format(input_c, local_var_name, local_var_name),
                    )
            else:
                writeln(
                    f, 2, '{}, &{}, sizeof({}));'.format(input_c, local_var_name, local_var_name)
                )
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


def gen_display_suite_connection(f, ip, output, input):
    # Compute SCADE Suite input characteristics
    input_instance_path = input.instancepath
    if input_instance_path == '':
        # The variable is not a probe, get the path of the operator owning the Scade variable
        input_instance_path = input.variable.owner.get_full_path()
    intput_subelement = fix_indexes(input.subelement)
    input_c = ip.get_generated_path(input_instance_path + input.name + intput_subelement)
    # Compute SCADE Display output characteristics
    output_spec = get_spec_from_basename(output.pathname)
    output_subelement = fix_indexes(output.subelement)
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
            declare_local_vars(
                f,
                input.variable.type,
                intput_subelement,
                local_var_name,
                output.object_type,
                output.type,
                output_spec.prefix + '_',
            )
            # project anonymous compound types
            if re.match(r'{.*}', input.type):
                writeln(
                    f,
                    2,
                    'kcg_assign(&{}, &({}){}, sizeof({}));'.format(
                        local_var_name, output_c, output_subelement, local_var_name
                    ),
                )
            elif isinstance(input.object_type, suite.Table):
                writeln(
                    f,
                    2,
                    'kcg_assign({}, ({}){}, sizeof({}));'.format(
                        local_var_name, output_c, output_subelement, local_var_name
                    ),
                )
            else:
                writeln(f, 2, '{} = {}{};'.format(local_var_name, output_c, output_subelement))
            convert_var(
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
                declare_local_vars(
                    f, fs.type, '', local_var_name, fd.type, output.type, output_spec.prefix + '_'
                )
                ouput_c = '{}_{}_G_{}({}_L_{}())'.format(
                    output_spec.prefix, output.layer, fd.name, output_spec.prefix, output.layer
                )
                field_class = fs.type
                while isinstance(field_class, suite.NamedType) and not field_class.is_predefined():
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
                convert_var(
                    f, 'input', 1, fs.type, '', local_var_name, input_c2, fd.type, output.pluggable
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


def gen_includes(f, project):
    writeln(f, 0, '/* SCADE Suite contexts */')
    writeln(f, 0, '#include "wuxctx%s.h"' % pathlib.Path(project.pathname).stem)
    writeln(f)
    writeln(f, 0, '/* SCADE Display includes */')
    writeln(f, 0, '#include <malloc.h>')
    if len(sdy_specifications):
        writeln(f, 0, '#include "sdy/sdy_events.h"')
        for spec in sdy_specifications:
            writeln(f, 0, '#include "sdy/{}.h"'.format(spec.prefix))
    writeln(f)
    writeln(f, 0, '#include "WuxSdyExt.h"')
    writeln(f)


def gen_init(f):
    count = len(sdy_specifications)
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
    for i, spec in enumerate(sdy_specifications):
        writeln(f, 1, '/* Init of {} */'.format(spec.prefix))
        writeln(f, 1, '_screens[%d].name = "%s";' % (i, pathlib.Path(spec.pathname).stem))
        writeln(f, 1, '_screens[%d].width = %s__screen_width();' % (i, spec.prefix))
        writeln(f, 1, '_screens[%d].height = %s__screen_height();' % (i, spec.prefix))
        writeln(f, 1, '_screens[%d].buffer = %s__init_buffer();' % (i, spec.prefix))
        writeln(
            f, 1, '_screens[{0}].size = _screens[{0}].width * _screens[{0}].height * 4;'.format(i)
        )
    writeln(f, 0, '}')
    writeln(f, 0, '#else')
    writeln(f, 0, 'void WuxSdyInit()')
    writeln(f, 0, '{')
    for spec in sdy_specifications:
        writeln(f, 1, '/* Init of {} */'.format(spec.prefix))
        writeln(f, 1, '{}__init();'.format(spec.prefix))
    writeln(f, 0, '}')
    writeln(f, 0, '#endif /* WUX_DISPLAY_AS_BUFFERS */')
    writeln(f)


def gen_draw(f):
    writeln(f, 0, '/* SCADE Display cycle */')
    writeln(f, 0, 'void WuxSdyDraw()')
    writeln(f, 0, '{')
    for spec in sdy_specifications:
        writeln(f, 1, '/* Draw of {} */'.format(spec.prefix))
        writeln(f, 1, '{}__draw();'.format(spec.prefix))
    writeln(f, 0, '}')
    writeln(f)


def gen_ios(f, ips):
    writeln(f, 0, '/* Connections Suite => Display */')
    writeln(f, 0, 'void WuxSdySetInputs()')
    writeln(f, 0, '{')
    if sdy_specifications:
        for spec in sdy_specifications:
            writeln(f, 1, '{}__lockio();'.format(spec.prefix))
        for op, ip in zip(sdy_mapping_operators, ips):
            if op:
                for item in op.mapping_items:
                    if isinstance(item.sender, displaycoupling.MappingVariable):
                        for input in item.receivers:
                            if isinstance(input, displaycoupling.MappingPlug):
                                gen_suite_display_connection(f, ip, item.sender, input)
        for spec in sdy_specifications:
            writeln(f, 1, '{}__unlockio();'.format(spec.prefix))
    writeln(f, 0, '}')
    writeln(f)
    writeln(f, 0, '/* Connections Suite <= Display */')
    writeln(f, 0, 'void WuxSdyGetOutputs()')
    writeln(f, 0, '{')
    if sdy_specifications:
        for spec in sdy_specifications:
            writeln(f, 1, '{}__lockio();'.format(spec.prefix))
        for op, ip in zip(sdy_mapping_operators, ips):
            if op:
                for item in op.mapping_items:
                    if isinstance(item.sender, displaycoupling.MappingPlug):
                        for input in item.receivers:
                            if isinstance(input, displaycoupling.MappingVariable):
                                gen_display_suite_connection(f, ip, item.sender, input)
        for spec in sdy_specifications:
            writeln(f, 1, '{}__unlockio();'.format(spec.prefix))
    writeln(f, 0, '}')
    writeln(f)


def gen_cancelled(f):
    writeln(f, 0, '/* SCADE Display cancelled */')
    writeln(f, 0, 'int WuxSdyCancelled()')
    writeln(f, 0, '{')
    for spec in sdy_specifications:
        writeln(f, 1, 'if ({}__cancelled()) return 1;'.format(spec.prefix))
    writeln(f, 1, 'return 0;')
    writeln(f, 0, '}')
    writeln(f)


def generate(f, target_dir, project, configuration, roots, ips):
    set_variables(project, configuration, roots)
    gen_includes(f, project)
    gen_init(f)
    gen_draw(f)
    gen_ios(f, ips)
    gen_cancelled(f)


# ----------------------------------------------------------------------------
# build
# ----------------------------------------------------------------------------


def build(target_dir, project, configuration):
    ok = True
    # generate in a sub directory to not have the header files deleted by
    # the generation process (bourrin) prior any generation
    sdy_target_dir = target_dir + '/sdy'
    try:
        os.mkdir(sdy_target_dir)
    except FileExistsError:
        pass
    # return ok
    for spec in sdy_specifications:
        sdy_project = os.path.abspath(spec.sdy_project.pathname)
        prefix = spec.prefix
        header = prefix + '.h'
        archive = prefix + '.a'
        log = os.path.join(os.path.abspath(sdy_target_dir), prefix + '.log')
        # path of the dll generated by SCADE Display/RP
        sdydll = os.path.join(os.path.abspath(sdy_target_dir), prefix + '.dll')
        # path of the dll once moved to target_dir
        dll = os.path.join(os.path.abspath(target_dir), prefix + '.dll')
        state_ext = 'wux_' + prefix
        up_to_date = sctoc.is_state_up_to_date(state_ext)
        state_files = sctoc.get_list_of_project_files([], sdy_project, spec.conf)
        state_files.append(dll)

        # Force rebuild
        if False:
            # TODO: JH: why force rebuild?
            try:
                os.remove(os.path.join(os.path.abspath(sdy_target_dir), header))
            except BaseException:
                pass
            try:
                os.remove(os.path.join(os.path.abspath(sdy_target_dir), archive))
            except BaseException:
                pass
        if False:
            # TODO: what is this about?
            # Create a batch file to execute the command (fixes issues with cygwin/bin in PATH)
            batch = os.path.join(os.path.abspath(sdy_target_dir), prefix + '.bat')
            with open(batch, 'w') as bf:
                if spec.sdy_project.is_rapid_proto():
                    bf.write(
                        '"{}\\bin\\ScadeRP.exe" batch generate "{}" -conf "{}" -source "{}" -outdir "{}" -prefix {}\n'.format(
                            sdy_rapidproto_home,
                            sdy_project,
                            spec.conf,
                            spec.get_name(),
                            os.path.abspath(sdy_target_dir),
                            prefix,
                        )
                    )
                else:
                    bf.write(
                        '"{}\\bin\\ScadeDisplayConsole.exe" batch generate "{}" -conf "{}" -source "{}" -outdir "{}" -prefix {}\n'.format(
                            sdy_display_home,
                            sdy_project,
                            spec.conf,
                            spec.get_name(),
                            os.path.abspath(sdy_target_dir),
                            prefix,
                        )
                    )
        # Generate
        if spec.sdy_project.is_rapid_proto():
            exe = '{}\\bin\\ScadeRP.exe'.format(sdy_rapidproto_home)
        else:
            exe = '{}\\bin\\ScadeDisplayConsole.exe'.format(sdy_display_home)
        try:
            if up_to_date:
                print_info('Skipping up_to_date graphical panel {}'.format(prefix))
                sctoc.add_generated_files('Graphical Panels', [pathlib.Path(dll).name])
            else:
                print_info('Generating graphical panel {}...'.format(prefix))
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
                    sctoc.add_generated_files('Graphical Panels', [pathlib.Path(dll).name])
                    # sctoc.add_object_files([archive], False)
                    print_info('Generation successful for {}.'.format(prefix))
                    sctoc.save_state(state_files, state_ext)
                else:
                    ok = False
                    print_info('Generation failed for {}.'.format(prefix))
        except BaseException:
            ok = False
            print_info('Unexpected error:', sys.exc_info()[0])
    if ok:
        other_dlls = ['d3dcompiler_47.dll', 'libEGL.dll', 'libGLESv2.dll']
        for dll in other_dlls:
            sdydll = os.path.join(os.path.abspath(sdy_target_dir), dll)
            if os.path.isfile(sdydll):
                dll = os.path.join(os.path.abspath(target_dir), dll)
                os.replace(sdydll, dll)
            if os.path.isfile(dll):
                sctoc.add_generated_files('Graphical Panels', [pathlib.Path(dll).name])
