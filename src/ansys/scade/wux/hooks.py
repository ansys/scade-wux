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

"""
Generic extension for defining Simulation C/C++ hooks.

* This activates WUX2_CTX and WUX2_SIMU_EXT.
* It does not have any settings and generates no code.
* It is up to the user to add the hooks implementation files
  to the SCADE Suite project.
"""

from scade.model.project.stdproject import Configuration, Project


class Hooks:
    """
    Implements the *C/C++ Simulation Hooks* (``WUX2_HOOKS``) extension.

    Refer to :ref:`Wrapper <usage/extension:Extension>` for its usage.

    Refer to *Generation Module* in the User Documentation,
    section *3/ Code Integration Toolbox/Declaring Code Generator Extension*.
    """

    @classmethod
    def get_services(cls):
        """Declare the generation service GoWrapper."""
        # the ID is meaningless, the service declared by this module
        # is activated automatically when the module is selected
        # in the Code Generator integration settings
        cls.instance = Hooks()
        hooks = (
            '<UNUSED WUX2_HOOKS>',
            ('-OnInit', cls.instance.init),
            # callback must be declared even if it is empty
            ('-OnGenerate', cls.instance.generate),
        )
        return [hooks]

    def init(self, target_dir: str, project: Project, configuration: Configuration):
        """
        Declare the required generation services and the execution order.

        Refer to *Generation Service* in section 3 of the *SCADE Python API Guide*
        in the SCADE Suite documentation.

        Parameters
        ----------
        target_dir : str
            Target directory for the code generation.

        project : Project
            Input SCADE Suite project.

        configuration : configuration
            SCADE Suite configuration selected for the code generation.
        """
        ctx = ('WUX2_CTX', ('-Order', 'Before'))
        simu_ext = ('WUX2_SIMU_EXT', ('-Order', 'Before'))
        return [ctx, simu_ext]

    def generate(self, target_dir: str, project: Project, configuration: Configuration):
        """
        Generate the code for this generation service.

        Refer to *Generation Service* in section 3 of the *SCADE Python API Guide*
        in the SCADE Suite documentation.

        Parameters
        ----------
        target_dir : str
            Target directory for the code generation.

        project : Project
            Input SCADE Suite project.

        configuration : configuration
            SCADE Suite configuration selected for the code generation.
        """
        # nothing to do
        return True
