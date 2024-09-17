# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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

These services can be included on demand by SCADE Code Generator targets or extensions.
"""

from ansys.scade.wux import __version__
import ansys.scade.wux.impl.a661 as a661
import ansys.scade.wux.impl.dllext as dllext
import ansys.scade.wux.impl.kcgcontext as kcgcontext
import ansys.scade.wux.impl.sdyext as sdyext
import ansys.scade.wux.impl.simuext as simuext


class WuxModule:
    """TODO."""

    # identification
    tool = 'Utility services for wrappers'
    version = __version__

    @classmethod
    def get_services(cls):
        """Declare all the provided utility services."""
        print(cls.tool, cls.version)
        services = []
        services.extend(kcgcontext.get_services())
        services.extend(sdyext.get_services())
        services.extend(a661.get_services())
        services.extend(simuext.get_services())
        services.extend(dllext.get_services())
        return services
