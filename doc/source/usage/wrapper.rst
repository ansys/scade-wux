Wrapper
=======

Overview
--------

The wrapper `Integration` is a SCADE target designed to host any number of
extensions. It has a behavior comparable to the SCADE Simulator:

* It manages the graphical panels, UAs and/or A661 server connections
  when available.
* It manages the registered extensions, for example instances of classes
  derived from ``CWuxSimulatorExtension`` through calls to the ``WuxXxx``
  simulation hooks.

The wrapper does not generate code: it provides the ``main`` function,
defined in ``WuxGoMain.cpp``, and declares a target to the build system with
the files from ``KCG``, ``WUX2`` generation services and all the extensions
selected in the Code Integration settings of the SCADE Code Generator tool.

The ``lib/WuxGoMain.cpp`` resource file is added to ``wux.sources``.

Interface
---------

The extensions can redefine the following functions:

.. code-block:: c++

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
* ``IntegrationStart``: ``argc``/``argv`` are the command line parameters
  of the executable, no filter is applied. Return `false` to stop the process.
* ``IntegrationStop``: Called just before the process terminates.
* ``SelfPaced``: Return ``true`` if the extension is scheduled by
  the environment.
* ``IsAlive``: Return ``false`` to stop the process.

Main loop period
----------------

When no extension is self-paced, the period is the one defined in the
Code Generator Integration settings; Else, the period can be specified
on the command line with the option ``-latency`` (ms) otherwise it is ``0``.

.. Note:
  The behavior is unclear when several extensions are registered and if at
  least one of them is self-paced.
  For a project involving conflicting extensions, we advise you provide a
  customized version of ``lib/WuxGoMain.cpp`` to implement the desired
  scheduling and interactions between the required extensions.
