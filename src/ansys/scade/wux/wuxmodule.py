# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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
SCADE Code Generation Module for utility SCADE Code Generation Services.

These :ref:`services <usage/services:generation services>` can be included
on demand by SCADE Code Generator extensions: target, adaptor or extension.
"""

from ansys.scade.wux import __version__
import ansys.scade.wux.impl.a661 as a661
import ansys.scade.wux.impl.dllext as dllext
import ansys.scade.wux.impl.kcgcontext as kcgcontext
import ansys.scade.wux.impl.proxyext as sdyproxy
import ansys.scade.wux.impl.sdyext as sdyext
import ansys.scade.wux.impl.simuext as simuext


class WuxModule:
    """
    Implements the generation module interface for ``WUX2_MODULE``.

    Refer to :ref:`usage/services:generation services` to for its usage.

    Refer to the *Generation Module* section in chapter 3 of the *SCADE Python API Guide*
    in the SCADE Suite documentation.
    """

    # identification
    _tool = 'Utility services for wrappers'
    _banner = '%s (%s)' % (_tool, __version__)

    @classmethod
    def get_services(cls):
        """Declare all the provided utility services."""
        print(cls._banner)
        services = []
        services.extend(kcgcontext.get_services())
        services.extend(sdyext.get_services())
        services.extend(a661.get_services())
        services.extend(simuext.get_services())
        services.extend(dllext.get_services())
        services.extend(sdyproxy.get_services())
        return services
