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

"""Generation of the contexts for SCADE suite root operators."""

from pathlib import Path

from scade.code.suite.mapping.c import MappingFile
import scade.code.suite.sctoc as sctoc
from scade.code.suite.wrapgen.c import InterfacePrinter
from scade.code.suite.wrapgen.model import MappingHelpers
from scade.model.project.stdproject import Configuration, Project

from ansys.scade.wux import __version__
import ansys.scade.wux.wux as wux
from ansys.scade.wux.wux import writeln


class _WuxInterfacePrinter(InterfacePrinter):
    """
    Fixes and enhancements to InterfacePrinter.

    * Simulation: Consider the simulator's contexts.
    * New services:

          * get_in_context_var
          * get_out_context_var
    """

    def __init__(self, mh, root, sep_ctx=False, indent='  ', simulation=False):
        """TODO."""
        super().__init__(mh, root, sep_ctx=sep_ctx, indent=indent)
        self.simulation = simulation

    def get_generated_path(self, var_path, subst=None):
        """TODO."""
        path = super().get_generated_path(var_path, subst=subst)
        if self.simulation:
            # TODO: code valid for standard generation only (no separate_io, no global_root_context, etc.)
            elems = path.split('.')
            if len(elems) > 1:
                ctx = 'outputs_ctx' if elems[1] == 'outC' else 'inputs_ctx'
                return ctx + '.' + '.'.join(elems[2:])
            else:
                # considering no global_root_context, must be a sensor
                # and thus, strange name decorations
                return '_ctx_%s_buffer' % path
        else:
            return path

    def get_in_context_var(self):
        """TODO."""
        ctx_acc = (
            '%s.%s' % (self._subst['wu_struct_var'], self._subst['inc_var'])
            if not self._sep_ctx and self._subst['wu_struct_var']
            else self._subst['inc_var']
        )
        return ctx_acc

    def get_out_context_var(self):
        """TODO."""
        ctx_acc = (
            '%s.%s' % (self._subst['wu_struct_var'], self._subst['ctx_var'])
            if not self._sep_ctx and self._subst['wu_struct_var']
            else self._subst['ctx_var']
        )
        return ctx_acc


class WuxContext:
    """
    Code Generator service for the integration.

    * Context management
    * Sensors definition
    * Periodicity
    * Call to the init, reset and cycle functions
    """

    ID = 'WUX2_CTX'
    tool = 'Context allocation for Scade root operators'
    banner = '%s (WUX %s)' % (tool, __version__)
    # prefix of genetared files
    # wuxctx instead of kcgctx: the files are not generated by KCG
    PREFIX = 'wuxctx'

    script_path = Path(__file__)
    script_dir = script_path.parent

    # settings
    user_sensors = False

    # options, may be overridden by clients
    simulation = False

    # files
    sources = []

    @classmethod
    def init(cls, target_dir: str, project: Project, configuration: Configuration):
        """TODO."""
        # KCG needed
        cg = ('Code Generator', ('-Order', 'Before'))
        return [cg]

    @classmethod
    def generate(cls, target_dir: str, project: Project, configuration: Configuration):
        """TODO."""
        print(cls.banner)

        # check simulation mode
        cls.set_simulation(project, configuration)

        # other settings
        cls.user_sensors = project.get_bool_tool_prop_def(
            'GENERATOR', 'USER_SENSORS_DECL', False, configuration
        )

        # initialize mf, mh and ips
        cls.set_globals(target_dir, project, configuration)

        basename = '%s%s' % (cls.PREFIX, Path(project.pathname).name)
        pathname = Path(target_dir) / basename
        pathheader = pathname.with_suffix('.h')
        sctoc.add_generated_files(cls.tool, [pathheader.name])
        with open(str(pathheader), 'w') as f:
            wux.gen_header(f, cls.banner)
            wux.gen_start_protect(f, pathheader.name)
            cls.gen_kcg_includes(f)
            cls.gen_contexts_declaration(f, project)
            wux.gen_end_protect(f, pathheader.name)
            wux.gen_footer(f)

        pathsource = pathname.with_suffix('.c')
        sctoc.add_generated_files(cls.tool, [pathsource.name])
        cls.sources.append(pathsource)
        with open(str(pathsource), 'w') as f:
            wux.gen_header(f, cls.banner)
            wux.gen_includes(f, [pathheader.name])
            cls.gen_contexts_definition(f)
            cls.gen_sensors(f)
            cls.gen_init(f)
            cls.gen_cycles(f)
            cls.gen_period(f)
            wux.gen_footer(f)

        # build
        cls.declare_target(target_dir, project, configuration)

        return True

    @classmethod
    def set_simulation(cls, project: Project, configuration: Configuration):
        """TODO."""
        enable_extensions = project.get_bool_tool_prop_def(
            'GENERATOR', 'ENABLE_EXTENSIONS', True, configuration
        )
        target = project.get_scalar_tool_prop_def(
            'GENERATOR', 'TARGET_ADAPTOR', 'Simulator', configuration
        )
        cls.simulation = enable_extensions and target == 'Simulator'

    @classmethod
    def set_globals(cls, target_dir: str, project: Project, configuration: Configuration):
        """TODO."""
        wux.mf = MappingFile((Path(target_dir) / 'mapping.xml').as_posix())
        wux.mh = MappingHelpers(wux.mf)
        roots = wux.mf.get_root_operators()
        wux.ips = []
        for index, root in enumerate(roots):
            ip = _WuxInterfacePrinter(wux.mh, root.get_scade_path(), simulation=cls.simulation)
            wux.ips.append(ip)

    @classmethod
    def gen_kcg_includes(cls, f):
        """TODO."""
        writeln(f, 0, '/* KCG generated files */')
        for ip in wux.ips:
            f.write(ip.print_includes())
        writeln(f)

    @classmethod
    def gen_contexts_declaration(cls, f, project):
        """TODO."""
        if cls.simulation:
            # cf. <project>_interface.h
            writeln(f, 0, '/* Simulator generated files */')
            writeln(f, 0, '#include "%s_interface.h"' % Path(project.pathname).stem)
            writeln(f, 0, '')
        else:
            writeln(f, 0, '/* contexts */')
            for ip in wux.ips:
                writeln(f, 0, ip.print_context_def().replace('  ', '    '))
                writeln(
                    f,
                    0,
                    'extern {wu_struct_type} {wu_struct_var};'.format_map(ip.get_substitutions()),
                )
            writeln(f)

    @classmethod
    def gen_contexts_definition(cls, f):
        """TODO."""
        writeln(f, 0, '/* contexts */')
        if not cls.simulation:
            for ip in wux.ips:
                writeln(
                    f, 0, '{wu_struct_type} {wu_struct_var};'.format_map(ip.get_substitutions())
                )
        writeln(f)

    @classmethod
    def gen_sensors(cls, f):
        """TODO."""
        sensors = wux.mf.get_all_sensors()
        if not cls.simulation and not cls.user_sensors and sensors:
            writeln(f, 0, '/* sensors */')
            for sensor in sensors:
                writeln(
                    f,
                    0,
                    '{0} {1};'.format(
                        sensor.get_type().get_generated().get_name(),
                        sensor.get_generated().get_name(),
                    ),
                )
        writeln(f)

    @classmethod
    def gen_init(cls, f):
        """TODO."""
        writeln(f, 0, '/* initializations */')
        writeln(f, 0, 'void WuxReset()')
        writeln(f, 0, '{')
        writeln(f, 0, '}')
        writeln(f)
        writeln(f, 0, 'void WuxInit()')
        writeln(f, 0, '{')
        if not cls.simulation:
            sep = ''
            for ip in wux.ips:
                f.write(sep)
                init = ip.print_context_init()
                if init != '':
                    f.write(init)
                    f.write('\n')
                call = ip.print_init_call(False)
                if call != '':
                    call = (
                        '\n'.join(['    ' + line for line in call.strip('\n').split('\n')]) + '\n'
                    )
                    f.write(call.replace('    #', '#   '))
                    # f.write(call)
                sep = '\n'
        writeln(f, 0, '}')
        writeln(f)

    @classmethod
    def gen_cycles(cls, f):
        """TODO."""
        writeln(f, 0, 'void WuxCycle()')
        writeln(f, 0, '{')
        if not cls.simulation:
            for ip in wux.ips:
                wux.write_indent(f, '    ', ip.print_cycle_call())
        writeln(f, 0, '}')
        writeln(f)

    @classmethod
    def gen_period(cls, f):
        """TODO."""
        writeln(f, 0, 'double WuxGetPeriod()')
        writeln(f, 0, '{')
        writeln(f, 0, '    return {0};'.format(sctoc.get_operator_sample_time()[0]))
        writeln(f, 0, '}')
        writeln(f)

    # ----------------------------------------------------------------------------
    # build
    # ----------------------------------------------------------------------------

    @classmethod
    def declare_target(cls, target_dir, project, configuration):
        """TODO."""
        wux.add_sources(cls.sources)
        # runtime files
        include = Path(cls.script_dir).parent / 'include'
        wux.add_includes([include])


# ----------------------------------------------------------------------------
# list of services
# ----------------------------------------------------------------------------


def get_services():
    """TODO."""
    wux_ctx = (WuxContext.ID, ('-OnInit', WuxContext.init), ('-OnGenerate', WuxContext.generate))
    return [wux_ctx]
