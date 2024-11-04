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

"""
A661 user applications integration code.

Extension for embedding UAs in other wrappers.
"""

import os
from pathlib import Path

import scade.code.suite.sctoc as sctoc

from ansys.scade.apitools.info import get_scade_home
from ansys.scade.wux import __version__
import ansys.scade.wux.wux as wux


class A661UAA:
    """Generation service for UA Adaptor (``WUX2_UAA``)."""

    ID = 'WUX2_UAA'
    tool = 'SCADE Suite UA Adaptor Extension'
    banner = '%s (WUX %s)' % (tool, __version__)

    # prefix of genetared files
    PREFIX = 'wuxuaa'

    script_path = Path(__file__)
    script_dir = script_path.parent

    ansys_scade_dir = get_scade_home()

    def __init__(self):
        # sources generated by this extension
        self.sources = []

        # a661 specs
        self.a661_specs = []
        self.ua_base_name = None
        self.host = None
        self.port = None
        self.config_file = None
        self.user_config = None

        # root operator (assume only one)
        self.root = None

    @classmethod
    def get_service(cls):
        """Declare the generation service UA Adaptor extension."""
        cls.instance = A661UAA()
        uaa = ('WUX2_UAA', ('-OnInit', cls.instance.init), ('-OnGenerate', cls.instance.generate))
        return uaa

    def init(self, target_dir, project, configuration):
        """Initialize the generation service."""
        cg = ('Code Generator', ('-Order', 'Before'))
        ctx = ('WUX2_CTX', ('-Order', 'Before'))
        return [cg, ctx]

    def generate(self, target_dir, project, configuration):
        """Generate the files."""
        print(self.banner)

        roots = wux.mf.get_root_operators()
        self.root = roots[0]

        self.set_a661_globals(target_dir, project, configuration)

        # run UA Adaptor if needed
        self.run_uua(target_dir, project, configuration)

        self.generate_interface(target_dir, project, configuration)

        self.declare_target(target_dir, project, configuration)

        return True

    # ------------------------------------------------------------------------
    # interface file with UA generated files
    # ------------------------------------------------------------------------

    def gen_includes(self, f, project):
        """Generate the include directives."""
        f.write('/* includes */\n')
        # f.write('#include <windows.h>\n')
        # f.write('\n')
        f.write('/* SCADE Suite contexts */\n')
        f.write('#include "wuxctx%s.h"\n' % Path(project.pathname).stem)
        f.write('\n')
        if self.ua_base_name is not None:
            f.write('/* UAA generated files */\n')
            f.write('#include "{0}.h"\n'.format(self.ua_base_name))
            f.write('\n')
        f.write('/* interface protocols */\n')
        if self.ua_base_name is not None:
            f.write('#include "A661Connect.h"\n')
        f.write('\n')
        f.write('#include "WuxA661Ext.h"\n')
        f.write('\n')

    def gen_connect(self, f):
        """Generate the call to connect to the server."""
        f.write('int WuxA661ConnectServer()\n')
        f.write('{\n')
        if self.ua_base_name is not None:
            f.write(
                '    return 0 /* OK */ == A661ConnectServer("{0}", {1});\n'.format(
                    self.host, self.port
                )
            )
        else:
            f.write('    return 1;\n')
        f.write('}\n')
        f.write('\n')

    def gen_disconnect(self, f):
        """Generate the call to disconnect from the server."""
        f.write('int WuxA661DisconnectServer()\n')
        f.write('{\n')
        if self.ua_base_name is not None:
            f.write('    return 0 /* OK */ == A661DisconnectServer();\n')
        else:
            f.write('    return 1;\n')
        f.write('}\n')
        f.write('\n')

    def gen_receive(self, f):
        """Generate the call to receive the messages."""
        f.write('void WuxA661ReceiveMessages()\n')
        f.write('{\n')
        if self.ua_base_name is not None:
            # assume only one root node
            ip = wux.ips[0]
            # extended ip, cf. kcgcontext.py
            inctxvar = ip.get_in_context_var()
            addr = 'NULL' if len(self.root.get_inputs()) == 0 or inctxvar == '' else '&' + inctxvar
            map = {'ua': self.ua_base_name, 'addr': addr}
            code = (
                '    static buffer_el msg[{ua}_MAX_SIZE_INPUT_BUFFER];\n'
                '    size_t len;\n'
                '\n'
                '    /* receive from server */\n'
                '    {ua}_decode_clear({addr});\n'
                '    len = A661Receive(msg, sizeof(msg));\n'
                '    if (len > 0)\n'
                '        {ua}_decode(msg, len, {addr});\n'
            )
            f.write(code.format_map(map))
        f.write('}\n')
        f.write('\n')

    def gen_send(self, f):
        """Generate the call to send the messages."""
        f.write('void WuxA661SendMessages()\n')
        f.write('{\n')
        if self.ua_base_name is not None:
            # assume only one root node
            ip = wux.ips[0]
            # extended ip, cf. kcgcontext.py
            outctxvar = ip.get_out_context_var()
            addr = (
                'NULL' if len(self.root.get_outputs()) == 0 or outctxvar == '' else '&' + outctxvar
            )
            map = {'ua': self.ua_base_name, 'addr': addr}
            code = (
                '    static buffer_el msg[{ua}_MAX_SIZE_OUTPUT_BUFFER];\n'
                '    size_t len;\n'
                '\n'
                '    len = {ua}_encode(msg, sizeof(msg), {addr});\n'
                '    /* send to server */\n'
                '    A661Send(msg, len);\n'
            )
            f.write(code.format_map(map))
        f.write('}\n')
        f.write('\n')

    def generate_interface(self, target_dir, project, configuration):
        """Generate the file."""
        path = Path(project.pathname)
        pathname = Path(target_dir) / (self.PREFIX + path.stem + '.c')
        sctoc.add_generated_files(self.tool, [pathname.name])
        self.sources.append(pathname)
        with open(str(pathname), 'w') as f:
            wux.gen_header(f, self.banner)
            self.gen_includes(f, project)
            # gen_kcg_declarations(f)
            # gen_period(f)
            # gen_init(f)
            # gen_cycle(f)
            self.gen_connect(f)
            self.gen_disconnect(f)
            self.gen_receive(f)
            self.gen_send(f)
            wux.gen_footer(f)

    # ------------------------------------------------------------------------
    # UA Adaptor
    # ------------------------------------------------------------------------

    def run_uua(self, target_dir, project, configuration):
        """Run UA Adaptor."""
        if self.ua_base_name is None:
            return
        uua = self.ansys_scade_dir / 'SCADE' / 'bin' / 'uaadaptor.exe'
        sdy = Path(wux.get_sdy_applications()[0].mapping_file.pathname).as_posix()
        trace = (Path(target_dir) / 'mapping.xml').as_posix()
        hdr = self.root.get_name() + '.h'
        # "%SCADE_DIR%\SCADE\bin\uaadaptor.exe" -sdy FuelManagementUA.sdy \
        # -n "%SCADE_DIR%/SCADE Display/config/a661_description/a661.xml" -outdir "UA" \
        # -k "KCG/kcg_trace.xml" -o "FuelManagementUA_FMUA_UA_1" \
        # -i "FuelManagementUA_interface.h"  -encoding "ASCII"  "../DF/FuelManagement.sgfx"
        uc = '' if self.user_config == '' else ' -user_config "{0}"'.format(self.user_config)
        command = (
            '"{uua}" -sdy "{sdy}" -n "{conf}" -outdir "{dir}" '
            '-k "{trace}" -o {base}{uc} -i "{hdr}" -encoding "ASCII" "{sgfx}"'.format(
                uua=uua,
                sdy=sdy,
                conf=self.config_file,
                dir=target_dir,
                trace=trace,
                base=self.ua_base_name,
                uc=uc,
                hdr=hdr,
                sgfx=Path(self.a661_specs[0].pathname).as_posix(),
            )
        )
        print(command)
        f = os.popen(command)
        stdout = f.read()
        for line in stdout.split('\n'):
            tokens = line.split(': ')
            if tokens[0] == 'I0006':
                path = Path(tokens[-1])
                if path.suffix == '.c':
                    self.sources.append(path)
                sctoc.add_generated_files('UA Adaptor', [path.name])
        if f.close() is not None:
            # error
            print(stdout)

    # ------------------------------------------------------------------------
    # build
    # ------------------------------------------------------------------------

    def declare_target(self, target_dir, project, configuration):
        """Update the makefile: sources and include search paths."""
        include = self.script_dir.parent / 'include'
        wux.add_includes([include])
        if len(self.sources) != 0:
            wux.add_sources(self.sources)
            # code has been generated, add A661Connect to the makefile
            lib = self.script_dir.parent / 'lib'
            wux.add_sources([lib / 'A661connect.c'])

    # ------------------------------------------------------------------------
    # settings
    # ------------------------------------------------------------------------

    def is_spec_a661(self, specification):
        """Return whether the specification is a A661 definition file."""
        project = specification.sdy_project
        return project is not None and project.is_uapc()

    def set_a661_globals(self, target_dir, project, configuration):
        """Get the A661 specifications."""
        # gather all the DF specifications and the configurations they are involved in
        uapc_projects = [
            _ for app in wux.get_sdy_applications() for _ in app.sdy_projects if _.is_uapc()
        ]
        # configurations is indexed by SCADE display configuration name and contains
        # the list of sources
        # note: if there are two projects with homonymous configurations, the lists are merged
        configurations = {}
        for uapc_project in uapc_projects:
            root = Path(uapc_project.pathname).parent
            for conf in uapc_project.project.configurations:
                sources = [
                    Path(os.path.abspath(root / _))
                    for _ in uapc_project.project.get_tool_prop_def('SDY', 'CONFSOURCE', [], conf)
                ]
                configurations.setdefault(conf.name, []).extend(sources)

        pairs = [
            _.split(',')
            for _ in project.get_tool_prop_def(
                'GENERATOR', 'DISPLAY_ENABLED_PANELS', [], configuration
            )
        ]
        # convert to a list of tuples
        root = Path(project.pathname).parent
        pairs = [(Path(os.path.abspath(root / _[0])), _[1]) for _ in pairs]
        # for old releases of SCADE, the first element is a specification,
        # for new ones, the first element is a project
        enabled_specs = set()
        for path, conf in pairs:
            if path.suffix.lower() == '.etp':
                # add the specifications for this configuration
                enabled_specs.update(configurations.get(conf, []))
            else:
                enabled_specs.add(path)

        for application in wux.get_sdy_applications():
            for specification in application.specifications:
                if (
                    self.is_spec_a661(specification)
                    and Path(specification.pathname) in enabled_specs
                ):
                    self.a661_specs.append(specification)

        if len(self.a661_specs) != 0:
            # assume one and only one root operator
            # TODO: what if several root operators?
            # TODO: what if both several specifications and root operators?
            specification = self.a661_specs[0]
            root = project.get_tool_prop_def('GENERATOR', 'ROOTNODE', [], configuration)[0]
            id = specification.application_id
            self.ua_base_name = '{0}_UA_{1}'.format(root.replace('::', '_'), id)
            self.host = project.get_scalar_tool_prop_def(
                'GENERATOR', 'A661_SERVER_IP', '127.0.0.1', configuration
            )
            self.port = project.get_scalar_tool_prop_def(
                'GENERATOR', 'A661_SERVER_PORT', '1231', configuration
            )
            self.config_file = Path(
                self.ansys_scade_dir / 'SCADE Display' / 'config' / 'a661_description' / 'a661.xml'
            ).as_posix()
            if project.get_bool_tool_prop_def(
                'GENERATOR', 'A661_USE_CUSTOM_CONFIG_FILE', False, configuration
            ):
                self.config_file = project.get_scalar_tool_prop_def(
                    'GENERATOR', 'A661_CONFIG_FILE_PATH', self.config_file, configuration
                )
                path = Path(self.config_file)
                if not path.is_absolute:
                    path = Path(project.pathname).joinpath(self.config_file)
                    self.config_file = path.resolve().as_posix()
            self.user_config = project.get_scalar_tool_prop_def(
                'GENERATOR', 'A661_USER_CONFIG', '', configuration
            )
            if self.user_config != '':
                path = Path(self.user_config)
                if not path.is_absolute:
                    path = Path(project.pathname).joinpath(self.user_config)
                    self.user_config = path.resolve().as_posix()


# ----------------------------------------------------------------------------
# list of services
# ----------------------------------------------------------------------------


def get_services():
    """Return the list of Generation services implemented by this module."""
    return [A661UAA.get_service()]
