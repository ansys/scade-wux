.. _contribute_scade_wux:

Contribute
##########

Overall guidance on contributing to a PyAnsys library appears in
`Contributing <https://dev.docs.pyansys.com/how-to/contributing.html>`_
in the *PyAnsys developer's guide*. Ensure that you are thoroughly familiar
with this guide before attempting to contribute to Ansys SCADE Wrapper Tools.

The following contribution information is specific to Ansys SCADE Wrapper Tools.

Install in developer mode
-------------------------
Installing Ansys SCADE Wrapper Tools in developer mode allows you to modify the
source and enhance it.

#. Clone the ``ansys-scade-wux`` repository:

   .. code:: bash

      git clone https://github.com/ansys/scade-wux

#. Access the ``scade-wux`` directory where the repository has been cloned:

   .. code:: bash

      cd scade-wux

#. Create a clean Python 3.10 environment and activate it:

   You can use the interpreter delivered with Ansys SCADE. For example,
   ``C:\Program Files\ANSYS Inc\v241\SCADE\contrib\Python310\python.exe``.

   .. code:: bash

      # Create a virtual environment
      python -m venv .venv

      # Activate it in a POSIX system
      source .venv/bin/activate

      # Activate it in Windows CMD environment
      .venv\Scripts\activate.bat

      # Activate it in Windows Powershell
      .venv\Scripts\Activate.ps1

#. Make sure that you have the latest required build system, documentation, testing,
   and CI tools:

   .. code:: bash

      python -m pip install -U pip     # Upgrading pip
      python -m pip install tox        # Installing tox (optional)
      python -m pip install .[build]   # for building the wheels
      python -m pip install .[tests]   # for testing the package
      python -m pip install .[doc]     # for building the documentation

#. Install `doxygen`_

   https://www.doxygen.nl/download.html

#. Install the project in editable mode:

   .. code:: bash

      python -m pip install --editable .

#. Use `tox`_ to verify your development installation:

   .. code:: bash

      tox

Unit test
---------
Ansys SCADE Wrapper Tools uses `tox`_ for testing. This tool allows you to
automate common development tasks (similar to ``Makefile``), but it is oriented
towards Python development.

Use ``tox``
^^^^^^^^^^^
While ``Makefile`` has rules, ``tox`` has environments. In fact, ``tox`` creates its
own virtual environment so that anything being tested is isolated from the project
to guarantee the project's integrity.

The following ``tox`` commands are provided:

- ``tox -e style``: Checks for coding style quality.
- ``tox -e py``: Checks for unit tests.
- ``tox -e py-coverage``: Checks for unit testing and code coverage.
- ``tox -e doc``: Checks for the documentation-building process.

Use raw testing
^^^^^^^^^^^^^^^
If required, from the command line, you can call style commands like
`ruff`_. You can also call unit testing commands like `pytest`_.
However, running these commands does not guarantee that your project is being tested in an
isolated environment, which is the reason why tools like ``tox`` exist.

Use ``pre-commit``
^^^^^^^^^^^^^^^^^^
Ansys SCADE Wrapper Tools follows the PEP8 standard as outlined in
`PEP 8 <https://dev.docs.pyansys.com/coding-style/pep8.html>`_ in
the *PyAnsys developer's guide* and implements style checking using
`pre-commit <https://pre-commit.com/>`_.

To ensure your code meets minimum code styling standards, run these commands::

  pip install pre-commit
  pre-commit run --all-files

You can also install this as a pre-commit hook by running this command::

  pre-commit install

This way, it's not possible for you to push code that fails the style checks::

  $ pre-commit install
  $ git commit -am "added my cool feature"
  Add License Headers......................................................Passed
  ruff.....................................................................Passed
  codespell................................................................Passed
  check for merge conflicts................................................Passed
  debug statements (python)................................................Passed
  check yaml...............................................................Passed
  trim trailing whitespace.................................................Passed

Build documentation
-------------------
For building documentation, you can run the usual rules provided in the
`Sphinx`_ ``make`` file. Here are some examples:

.. code:: bash

    #  build and view the doc from the POSIX system
    make -C doc/ html && your_browser_name doc/html/index.html

    # build and view the doc from a Windows environment
    .\doc\make.bat clean
    .\doc\make.bat html
    start .\doc\_build\html\index.html

However, the recommended way of checking documentation integrity is to use
``tox``:

.. code:: bash

    tox -e doc-html && your_browser_name .tox/doc_out/index.html

Debug and integration test
--------------------------
Ansys SCADE Wrapper Tools needs to be registered to SCADE for integration testing.
Indeed, the generation modules are called from a SCADE code generator session.

Install in user mode
^^^^^^^^^^^^^^^^^^^^
It is not possible to reuse the virtual environment setup for the repository.
You must install the package in an environment accessible by SCADE, e.g. its
own Python distribution, although this is not advised, or the Python 3.10
*user* distribution:

.. code:: bash

   <python310.exe>  -m pip install --user --editable .

*You can reuse any ``<install>\SCADE\contrib\Python310\python.exe``
or Python 3.10 installation on your computer.*

If you are using Ansys SCADE 2024 R2 or below, you must perform one additional
step, to install a registration file in ``%APPDATA%\SCADE\Customize``:

.. code:: bash

   <python310.exe>  -m ansys.scade.wux.register

Debug
^^^^^
The ``.\tests\Debug\debug.py`` script uses internal SCADE Code Generator entry points
to start a debug session for the scripts.

You must use the Python 3.10 environment delivered with SCADE, located in
``<install>\contrib\Python310``.

For example:
``C:\Program Files\ANSYS Inc\v251\SCADE\contrib\Python310``.

Configure PYTHONPATH to refer to ``<install>\SCADE\bin`` and
``<install>\SCADE\APIs\Python\lib``. For example:

.. code:: bash

   set PYTHONPATH=C:\Program Files\ANSYS Inc\v251\SCADE\SCADE\bin;C:\Program Files\ANSYS Inc\v251\SCADE\SCADE\APIs\Python\lib

Refer to ``.\tests\Debug\debug.py`` for its command line parameters.

Run the integration tests
^^^^^^^^^^^^^^^^^^^^^^^^^
These are manual tests. Refer to the test procedures, contained in each test
directory as readme files.

Uninstall
^^^^^^^^^
Once the test or debug sessions are completed, you may uninstall the package
as follows:

.. code:: bash

   python -m pip uninstall ansys.scade.wux

If you are using Ansys SCADE 2024 R2 or below, you should remove the
registration file:

.. code:: bash

   del %APPDATA%\SCADE\Customize\wux.srg

Distribute
----------
If you would like to create either source or wheel files, start by installing
the building requirements and then executing the build module:

.. code:: bash

    python -m pip install .[build]
    python -m build
    python -m twine check dist/*

Post issues
-----------
Use the `Ansys SCADE Wrapper Tools Issues <https://github.com/ansys/scade-wux/issues>`_
page to submit questions, report bugs, and request new features. When possible, use
these templates:

* Bug, problem, error: For filing a bug report
* Documentation error: For requesting modifications to the documentation
* Adding an example: For proposing a new example
* New feature: For requesting enhancements to the code

If your issue does not fit into one of these template categories, click
the link for opening a blank issue.

To reach the project support team, email `pyansys.core@ansys.com <pyansys.core@ansys.com>`_.

.. LINKS AND REFERENCES

.. _tox: https://tox.wiki/en/4.12.0/
.. _ruff: https://github.com/astral-sh/ruff
.. _pip: https://pypi.org/project/pip/
.. _pre-commit: https://pre-commit.com/
.. _pytest: https://docs.pytest.org/en/stable/
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _wheel file: https://github.com/ansys/scade-wux/releases
.. _doxygen: https://www.doxygen.nl/
