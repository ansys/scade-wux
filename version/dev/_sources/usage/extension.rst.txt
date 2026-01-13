Extension
=========

Overview
--------

The ``C/C++ Simulation Hooks`` extension is a SCADE extension that
bundles :ref:`Simulator extension <usage/services:Simulator extension>` and
:ref:`Context <usage/services:Context>` generation services.
It does not generate code.

It avoids defining a Code Generator extension when you don't need to
generate integration code from the model.

Usage
-----

Once the extension is activated, you can add your own simulation hooks
implemented as classes derived from ``CWuxSimulatorExtension``:

* Create a C++ file defining an instance of ``CWuxSimulatorExtension`` and
  override the required functions.

  Refer to :ref:`Simulator extension <usage/services:Simulator extension>`
  for details.
* Add the file to your project.
* Declare it as *Source File for C*.
