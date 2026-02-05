Getting started
===============
To use Ansys SCADE Wrapper Tools, you must have a valid license for Ansys SCADE.

For information on getting a licensed copy, see the
`Ansys SCADE Suite <https://www.ansys.com/products/embedded-software/ansys-scade-suite>`_
page on the Ansys website.

Requirements
------------
The ``ansys-scade-wux`` package supports only the versions of Python delivered with
Ansys SCADE, starting from 2023 R2:

* 2023 R2 and later: Python 3.10

Install in user mode
--------------------
The following steps are for installing Ansys SCADE Wrapper Tools in user mode.
If you want to contribute to Ansys SCADE Wrapper Tools,
see :ref:`contribute_scade_wux` for the steps for installing in developer mode.

#. Before installing Ansys SCADE Wrapper Tools in user mode, run this command
   to ensure that you have the latest version of `pip`_:

   .. code:: bash

      python -m pip install -U pip

#. Run this command to install Ansys SCADE Wrapper Tools:

   .. code:: bash

       python -m pip install --user ansys-scade-wux

#. For Ansys SCADE releases 2024 R2 and below, run this command to complete the installation:

   .. code:: bash

      python -m ansys.scade.wux.register

   .. Note::

      This additional step is not required when installing the package with
      Ansys SCADE Extension Manager.

.. LINKS AND REFERENCES
.. _pip: https://pypi.org/project/pip/
