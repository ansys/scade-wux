.. _ref_release_notes:

Release notes
#############

This document contains the release notes for the project.

.. vale off

.. towncrier release notes start

`2.2.0 <https://github.com/ansys/scade-wux/releases/tag/v2.2.0>`_ - September 02, 2025
======================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Feat: Add a bundle extension for defining C/C++ simulation hooks.
          - `#43 <https://github.com/ansys/scade-wux/pull/43>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - fix: Limit flit version
          - `#25 <https://github.com/ansys/scade-wux/pull/25>`_

        * - fix: Add the SCADE Display proxy generated file to the list of integration files
          - `#31 <https://github.com/ansys/scade-wux/pull/31>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Fix: enhance robustness
          - `#34 <https://github.com/ansys/scade-wux/pull/34>`_

        * - Ci: bump ansys/actions from 8 to 10 in the actions group
          - `#35 <https://github.com/ansys/scade-wux/pull/35>`_

        * - Ci: bump the actions group with 2 updates
          - `#36 <https://github.com/ansys/scade-wux/pull/36>`_, `#45 <https://github.com/ansys/scade-wux/pull/45>`_

        * - Build(deps): bump the dependencies group with 8 updates
          - `#37 <https://github.com/ansys/scade-wux/pull/37>`_

        * - Docs: update ``contributors.md`` with the latest contributors
          - `#38 <https://github.com/ansys/scade-wux/pull/38>`_

        * - Docs: Update ``CONTRIBUTORS.md`` with the latest contributors
          - `#39 <https://github.com/ansys/scade-wux/pull/39>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - chore: update CHANGELOG for v2.1.0
          - `#21 <https://github.com/ansys/scade-wux/pull/21>`_

        * - chore: update CHANGELOG for v2.1.1
          - `#24 <https://github.com/ansys/scade-wux/pull/24>`_

        * - chore: update CHANGELOG for v2.1.3
          - `#29 <https://github.com/ansys/scade-wux/pull/29>`_


`2.1.3 <https://github.com/ansys/scade-wux/releases/tag/v2.1.3>`_ - April 30, 2025
==================================================================================

.. tab-set::


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - fix: Blocking issues
          - `#28 <https://github.com/ansys/scade-wux/pull/28>`_


`2.1.1 <https://github.com/ansys/scade-wux/releases/tag/v2.1.1>`_ - March 20, 2025
==================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - feat: Add register and unregister entry points for Extensions Manager
          - `#22 <https://github.com/ansys/scade-wux/pull/22>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - ci: Specify the version of Python for updating the change log
          - `#23 <https://github.com/ansys/scade-wux/pull/23>`_


`2.1.0 <https://github.com/ansys/scade-wux/releases/tag/v2.1.0>`_ - 2025-01-20
==============================================================================

Added
^^^^^

- feat: technical review `#17 <https://github.com/ansys/scade-wux/pull/17>`_


Fixed
^^^^^

- fix: Avoid name conflict with legacy WrapUtilsEx 1.x `#19 <https://github.com/ansys/scade-wux/pull/19>`_
- fix: changelog action inputs `#20 <https://github.com/ansys/scade-wux/pull/20>`_


Documentation
^^^^^^^^^^^^^

- chore: update CHANGELOG for v2.0.1 `#12 <https://github.com/ansys/scade-wux/pull/12>`_
- chore: update CHANGELOG for v2.0.2 `#14 <https://github.com/ansys/scade-wux/pull/14>`_
- docs: doc review `#15 <https://github.com/ansys/scade-wux/pull/15>`_
- docs: Add minimal doc-strings for test stubs and implementation files `#16 <https://github.com/ansys/scade-wux/pull/16>`_


Test
^^^^

- test: Complete unit tests for SCADE Suite - SCADE Display connections `#18 <https://github.com/ansys/scade-wux/pull/18>`_

`2.0.2 <https://github.com/ansys/scade-wux/releases/tag/v2.0.2>`_ - 2024-10-10
==============================================================================

Maintenance
^^^^^^^^^^^

- Refactor: Perform a separate registration for SCADE releases based on Python 3.7 or 3.10 `#13 <https://github.com/ansys/scade-wux/pull/13>`_

`2.0.1 <https://github.com/ansys/scade-wux/releases/tag/v2.0.1>`_ - 2024-10-06
==============================================================================

Fixed
^^^^^

- fix: Add an action to update the change log before creating a release `#8 <https://github.com/ansys/scade-wux/pull/8>`_


Documentation
^^^^^^^^^^^^^

- maint: Finalize the configuration `#6 <https://github.com/ansys/scade-wux/pull/6>`_
- ci: fix change log `#9 <https://github.com/ansys/scade-wux/pull/9>`_
- refactor: Refactor the classes and code to enhance reusability and testability `#10 <https://github.com/ansys/scade-wux/pull/10>`_


Maintenance
^^^^^^^^^^^

- ci: Fix the url for coverage `#7 <https://github.com/ansys/scade-wux/pull/7>`_

.. vale on
