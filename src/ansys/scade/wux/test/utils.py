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

"""Provides utility classes and methods for testing wrappers."""

from scade.model.project.stdproject import Configuration, Project

from ansys.scade.wux.test.sctoc_stub import reset_stub
import ansys.scade.wux.wux as wux


class ServiceProxy:
    """
    Provides an interface for generation services.

    Parameters
    ----------
    cls: type
        Class defining the service, that must provide the get_services method.
    """

    def __init__(self, cls: type) -> None:
        services = cls.get_services()
        assert len(services) == 1
        callbacks = {n: m for (n, m) in services[0][1:]}
        self.init = callbacks.get('-OnInit')
        self.generate = callbacks.get('-OnGenerate')
        self.build = callbacks.get('-OnBuild')

    def init(self, target_dir: str, project: Project, configuration: Configuration):
        """Call the service's initialization function, if defined."""
        return self.init(target_dir, project, configuration) if self.init else []

    def generate(self, target_dir: str, project: Project, configuration: Configuration) -> bool:
        """Call the service's initialization function, if defined."""
        return self.generate(target_dir, project, configuration) if self.generate else True

    def build(self, target_dir: str, project: Project, configuration: Configuration) -> bool:
        """Call the service's initialization function, if defined."""
        return self.build(target_dir, project, configuration) if self.build else True


def reset_test_env():
    """Reset the global variables for a new test."""
    wux.reset()
    reset_stub()
