Wrapper
=======

Overview
--------

The wrapper ``Generic Integration`` is a SCADE target designed to host any
number of extensions. It has a behavior comparable to the SCADE Simulator:

* It manages the graphical panels, UAs and/or A661 server connections
  when available.
* It manages the registered extensions, for example instances of classes
  derived from ``CWuxSimulatorExtension`` through calls to the ``WuxXxx``
  simulation hooks.

The wrapper does not generate code: it provides the ``main`` function,
defined in ``WuxGoMain.cpp``, and declares a target to the build system with
the files generated by ``KCG`` and those added by the generation services with
the tag ``WUX``.

The ``lib/WuxGoMain.cpp`` resource file is declared to the Code Generator
with the tag ``WUX``.

Interface
---------

The extensions can redefine the following functions:

.. code-block:: cpp

  class CWuxSimulatorExtension
  {
  public:
      ...
      // integration interface
      virtual const char* GetIdent();
      virtual bool IntegrationStart(int argc, char* argv[]);
      virtual void IntegrationStop();
      virtual bool SelfPaced();
      virtual bool IsAlive();
      ...
  };

* ``GetIdent``: Identifier of the extension, for error reporting or
  discrimination.
* ``IntegrationStart``: ``argc``/``argv`` are the command line parameters of
  the executable, no filter is applied. Returns ``false`` to stop the process.
* ``IntegrationStop``: Called just before the process terminates.
* ``SelfPaced``: Returns ``true`` if the extension is scheduled by
  the environment, for example by waiting for some event in the
  ``BeforeSimStep`` function.
* ``IsAlive``: Returns ``false`` to stop the process.

Refer to :ref:`usage/services:Simulator extension` for more information about
the ``CWuxSimulatorExtension`` class.

Main loop period
----------------

When no extension is self-paced, the period is the one defined in the
Code Generator Integration settings; Else, the period can be specified
on the command line with the option ``-latency`` (ms) otherwise it is ``0``.

.. Note::

   The behavior is unclear when several extensions are registered and if at
   least one of them is self-paced.
   For a project involving conflicting extensions, it is advised to provide a
   customized version of ``lib/WuxGoMain.cpp`` to implement the desired
   scheduling and interactions between the required extensions.
