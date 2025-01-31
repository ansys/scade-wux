Generation services
===================

Overview
--------

The class :py:mod:`WuxModule <ansys.scade.wux.wuxmodule.WuxModule>` defines
the ``WUX2_MODULE`` generation module. Its generation services are not visible
to the end user; they must be explicitly requested by client wrappers.

The module registers all the generation services included to the Code Generator.

Ansys SCADE Wrapper Tools provide the following generation services,
detailed in the next sections:

* :ref:`Context allocation for Scade root operators <usage/services:Context>` (``WUX2_CTX``):

  * Instantiates ``MappingFile``, ``MappingHelper`` and ``InterfacePrinter``
    for the root operators.
  * Generates the header/source files for declaring/defining SCADE generated code contexts.

    **Note**: The current version is not expected to support options like
    ``separate_io``, ``global_root_context`` or root functions returning a scalar value.

  * Generates the ``Init``, ``Reset``, and ``Cycle`` functions that call the
    corresponding functions for all the root operators.
  * Generates a ``GetPeriod`` function for accessing the period specified in
    the code integration settings.

* :ref:`SCADE Suite-Display Extension <usage/services:Display extension>` (``WUX2_SDY``):

  * Generates the glue code for connecting the generated code from the graphical panels and the SCADE models.

* :ref:`SCADE Display Proxy Extension <usage/services:Display proxy extension>` (``WUX2_SDY_PROXY``):

  * Builds the SCADE Display and SCADE Rapid Prototyper DLLs.
  * Generates proxies for loading the DLLs (avoids link editing and compiler issues).

* :ref:`SCADE Suite UA Adaptor Extension <usage/services:UA Adaptor extension>` (``WUX2_UAA``):

  * Runs UA Adaptor for the (only one) root operator.
  * Generates the glue code for sending and receiving A661 messages.

* :ref:`Extension for SCADE Simulator's extensions <usage/services:Simulator extension>` (``WUX2_SIMU_EXT``):

  * Compatible with graphical panels.
  * Avoids defining ``DllMain`` for simulation start and stop hooks.

* :ref:`Extension for DllMain services <usage/services:DllMain extension>` (``WUX2_DLL_EXT``):

  * Allows several extensions to register to DllMain's hooks.

Context
-------

This service (``WUX2_CTX``) manages the integration of a root operator.
It generates the following files:

* ``wuxctx<project name>.h``

  * Declaration of the contexts for the root operators.
  * Reference to `<project name>_interface.h` instead of declaring
    new contexts when the current Target is the SCADE Simulator.

* ``wuxctx<project name>.c``

  * Allocation of the contexts when the current Target is not the
    SCADE Simulator, otherwise nothing.
  * Generation of the functions :cpp:func:`WuxInit`, :cpp:func:`WuxReset` and
    :cpp:func:`WuxCycle`.
    These functions call the related code for each root operator, when the
    current Target is not the SCADE Simulator, otherwise they are empty.
  * Generation of the :cpp:func:`WuxGetPeriod` function that returns the
    period declared in the Code Integration settings.
    The returned value is in seconds.

All the generated functions are declared in the :std:doc:`/runtime/ctxext`
resource file and its containing directory is added to the Code Generator.

This generation service initializes the :py:data:`ips <wux.ips>`,
:py:data:`mf <wux.mf>` and :py:data:`mh <wux.mh>` global variables of the
:py:mod:`wux <ansys.scade.wux.wux>` module. Note that the
:py:data:`ips <wux.ips>` collection contains instances of a class derived from
``InterfacePrinter``, that considers the SCADE Simulator's context when the
code generation target is ``Simulator``.

Display extension
-----------------

This service (``WUX2_SDY``) is responsible for generating the glue code
between SCADE Suite and SCADE Display.

It generates the following file:

* ``<project name>_sydext.c``:

  * ``void WuxSdyInit()``: Initializes the displays.
  * ``void WuxSdyDraw()``: Draws the displays.
  * ``void WuxSdySetInputs()``: Copies the mapped values from the contexts to the layers.
  * ``void WuxSdyGetOutputs()``: Copies the mapped values from the layers to the contexts.
  * ``int WuxSdyCancelled()``: Returns ``1`` if one of the display is closed.

The generated files are declared to the Code Generator with the tag ``WUX``.

.. Note::

   The functions are always generated to avoid link errors, but are
   empty if no graphical panel is referenced in the configuration.

All the generated functions are declared in :std:doc:`/runtime/sdyext`,
and the containing directory is declared to the Code Generator.

Display proxy extension
-----------------------

This service (``WUX2_SDY_PROXY``) is responsible for building the DLLs for each
graphical panel referenced in the configuration, and for providing functions to load
the DLLs at runtime.

It generates the following file:

* ``<project name>_sydextprx.cpp``:

  * ``int WuxLoadSdyDlls(/*HINSTANCE*/ void* hinstDll)``: Loads all the displays.
  * ``int WuxUnloadSdyDlls(/*HINSTANCE*/ void* hinstDll)``: Unoads all the displays.

The generated files are declared to the Code Generator with the tag ``WUX``.

.. Note::

   The functions are always generated to avoid link errors, but are
   empty if no graphical panel is referenced in the configuration.

All the generated functions are declared in :std:doc:`/runtime/sdyproxy`,
and the containing directory is declared to the Code Generator.

The ``lib/WuxSdyProxy.cpp`` resource file is required and is declared to the
Code Generator with the tag ``WUX``.

UA Adaptor extension
--------------------

This service (``WUX2_UAA``) is responsible for generating the definition files
(DF) files for each A661 panel referenced in the configuration, for running
SCADE UA Adaptor for the root operators, and for providing functions to
send/receive A661 messages at runtime.

It generates the following functions in ``wuxuaa<project name>.c``:

* ``int WuxA661ConnectServer()``: Connects to the A661 server,
  and return 0 on success.
* ``int WuxA661DisconnectServer()``: Disconnects from the A661 server,
  and return 0 on success.
* ``void WuxA661ReceiveMessages()``: Receives the A661 messages,
  and copies the mapped values to the contexts.
* ``void WuxA661SendMessages()``: Gets the mapped values form the contexts,
  and sends all the A661 messages.

The generated file as well as the files generated by SCADE UA Adaptor are
declared to the Code Generator with the tag ``WUX``.

.. Note::

   The functions are always generated to avoid link errors,
   but are empty if no UA is referenced in the configuration.

All the generated functions are declared in :std:doc:`/runtime/a661ext`,
and the containing directory is declared to the Code Generator.

The ``lib/A661Connect.c`` resource file is required and is declared to the
Code Generator with the tag ``WUX``.

Simulator extension
-------------------

.. Note::

   This generation service was initially designed to allow the
   usage of SCADE Simulator with one or more wrappers together with
   SCADE graphical panels.
   It was then extended to provide a generic way for integrating extensions
   with the Wrapper :std:doc:`Generic Integration </usage/wrapper>`.
   It was not renamed for compatibility reasons.
   The following text describes the connection to the SCADE Simulator but this
   applies to any host.

This generation service (``WUX2_SIMU_EXT``) does not generate new files, but
provides a workaround for a limitation of the SCADE Simulator interface.
Indeed, the SCADE Simulator allows hooks thanks to functions like
``BeforeSimInit``, ``BeforeSimStep``, or ``AfterSimStep``, when the
preprocessor variable ``EXTENDED_SIM`` is defined.
This allows wrapping code, such as communications with external
environments, to be executed in the SCADE Simulator without requiring imported
operators for the I/Os.

Unfortunately, if the wrapping code is used together with graphical panels,
the existing hook mechanism is not enough: two different pieces of code define
the same functions, leading to link errors.

The purpose of this generation service is to patch the file
``<project name>_interface.c`` generated by the SCADE Simulator Wrapper
so that:

* the file includes :std:doc:`/runtime/simuext`
* ``EXTENDED_SIM`` is always defined in this file
* all the calls to a ``Xxx`` hook function are replaced by calls to a
  ``WuxXxx`` function

The ``WuxXxx`` functions are declared in :std:doc:`/runtime/simuext` and the
containing directory is declared to the Code Generator. They are implemented
in the ``lib/WuxSimuExt.cpp`` resource file that is required, and declared to
the Code Generator with the tag ``WUX``. The implementation consists in
calling the function for each registered extension.

The wrappers that want to hook the SCADE Simulator, or to be compatible with
the :std:doc:`Generic Integration </usage/wrapper>` wrapper, must create a
static instance of a class deriving from :cpp:class:`CWuxSimulatorExtension`.

* The constructor automatically registers the instance to the list of hooks.
  All the functions have an empty implementation by default.
* When ``EXTENDED_SIM`` is defined, the source defines a specific instance of
  :cpp:class:`CWuxSimulatorExtension` that calls the former global hooks to ensure the
  compatibility with the existing services, especially the simulation with
  graphical panels.

The example hereafter shows the usage of this feature by some wrapper:

.. code-block:: cpp

  static class MySimulatorExtension : public CWuxSimulatorExtension
  {
  public:
      MySimulatorExtension()
          : m_participant(NULL), m_bInitialized(false)
      {
      }

      void BeforeSimInit()
      {
          if (!m_bInitialized) {
              m_participant = CreateParticipant();
              m_bInitialized = true;
          }
      }

      void BeforeSimStep()
      {
          if (m_participant != NULL) {
              _ReadData();
          }
      }

      void AfterSimStep()
      {
          if (m_participant != NULL) {
              _WriteData();
          }
      }

      void ExtendedSimStop()
      {
          DeleteParticipant(m_participant);
      }

  protected:
      Participant* m_participant;
      bool m_bInitialized;
  } mySimulatorExtension;

* The ``_ReadData()`` function retrieves data from the environment and copies
  the values to the context of the root operators.
  The ``_WriteData()`` function does the reverse.
* The initialization/termination of the external environment has no more to be
  done in ``DllMain``, which often leads to thread issues.

This design allows using graphical panels in the Simulation. Or not.

.. Note::

   All target wrappers embedding these extensions must define the preprocessor
   directive ``WUX_STANDALONE``. In other words, the macro ``WUX_STANDALONE``
   is not defined if and only if the extension is used in the context of the
   SCADE Simulator.

DllMain extension
-----------------

This generation service (``WUX2_DLL_EXT``) does not generate new files,
but allows several services to subscribe to ``DllMain``. It is used by
generation services that produce a DLL instead of a standalone executable.

A wrapper which needs an access to ``DllMain`` must include
:std:doc:`/runtime/dllext` and define a static instance of a class deriving
from :cpp:class:`CWuxDllInstance`.

* The constructor automatically registers the instance to the list of hooks.
* All the functions have an empty implementation by default.

The directory containing :std:doc:`/runtime/dllext` is declared to the
Code Generator.

The ``lib/WuxDllExt.cpp`` resource file is declared to the Code Generator with
the tag ``WUX``.
