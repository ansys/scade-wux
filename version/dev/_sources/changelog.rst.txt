.. _ref_release_notes:

Release notes
#############

This document contains the release notes for the project.

.. vale off

.. towncrier release notes start

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
