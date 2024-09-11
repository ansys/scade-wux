Generation services
===================

Overview
--------

The class ``ansys.scade.wux.module.WuxModule`` defines the
generation module ``WUX2_MODULE``. Its generation services are not visible
to the end user: They must be explicitly requested by client wrappers.

The module registers all the included generation services to the Code Generator.


{{Title}} provides the following generation services:

* Context allocation for Scade root operators (``WUX2_CTX``):

  * Instantiate ``MappingFile``, ``MappingHelper`` and ``InterfacePrinter``
    for the root operators(s).
  * Generate the header/source files for declaring/defining for SCADE generated code contexts.

    **Note**: The current version is not expected to support options like
    ``separate_io``, ``global_root_context`` or root functions returning a scalar value.

  * Generate the ``Init``, ``Reset``, and ``Cycle`` functions that call the
    corresponding functions for all the root operators.
  * Generate a ``GetPeriod`` function for accessing the period specified in
    the code integration settings.

* SCADE Suite-Display Extension (``WUX2_SDY``):

  * Build the SCADE Display and SCADE Rapid Prototyper DLLs.
  * Generate the glue code for connecting the generated code from the graphical panels and the SCADE models.
  * Generate proxies for loading the DLLs (avoid link edition and compiler issues).

* SCADE Suite UA Adaptor Extension (``WUX2_UUA``):

  * Run UA Adaptor for the (only one) root operator.
  * Generate the glue code for sending and receiving A661 messages.

* Extension for SCADE Simulator's extensions (``WUX2_SIMU_EXT``):

  * Compatible with graphical panels.
  * Avoid defining ``DllMain`` for simulation start and stop hooks .

* Extension for DllMain services (``WUX2_DLL_EXT``):

  * Allows several extensions to register to DllMain's hooks.

.. TODO: link to the sections below

Refer to the next sections for a complete reference.

Context allocation for Scade root operators (``WUX2_CTX``)
----------------------------------------------------------

This service generates the following files:

* ``wuxctx<project name>.h``

  * Declaration of the contexts for the root operators.
  * Reference to `<project name>_interface.h` instead of declaring
    new contexts when the current Target is the Simulator.

* ``wuxctx<project name>.c``

  * Allocation of the contexts when the current Target is not the Simulator,
    otherwise nothing.
  * Generation of the functions ``WuxInit``, ``WuxReset`` and ``WuxCycle``.
    These functions call the related code for each root operator, when the
    current Target is not the SCADE Simulator, otherwise they are empty.
  * Generation of the ``WuxGetPeriod`` function that returns the period
    declared in the Code Integration settings.
    The returned value is in ms.

All the generated functions are declared in the ``include/WuxCtxExt.h``,
resource file and its containing directory is added to ``wux.includes``.

This generation service initializes the variables ``mf``, ``mh`` and ``ips``
of the global variable `wux`. Note that the collection ``ips`` contains
instances of a derived class of ``InterfacePrinter``,
``_WuxInterfacePrinter``n that considers the SCADE Simulator's context when
the code generation target is ``Simulator``.

SCADE Suite-Display Extension (``WUX2_SDY``)
--------------------------------------------

This service is responsible for building the DLLs for each graphical panel
referenced in the configuration, generating the glue code between SCADE Suite
and SCADE Display, and providing functions to load the DLLs at runtime.

It generates the following functions spread in two files:

* ``<project name>_sydext.c``:

  * ``void WuxSdyInit()``: Initialize the displays.
  * ``void WuxSdyDraw()``: Draw the displays.
  * ``void WuxSdySetInputs()``: Copy the mapped values from the contexts to the layers.
  * ``void WuxSdyGetOutputs()``: Copy the mapped values from the layers to the contexts.
  * ``int WuxSdyCancelled()``: Return `1` if one of the display is closed.

* ``<project name>_sydextprx.cpp``:

  * ``int WuxLoadSdyDlls(/*HINSTANCE*/ void* hinstDll)``: Load all the displays.
  * ``int WuxUnloadSdyDlls(/*HINSTANCE*/ void* hinstDll)``: Unoad all the displays.

The generated files are added to ``wux.sources``.

**Note**: The functions are always generated to avoid link errors,
but are empty if no graphical panel is referenced in the configuration.

All the generated functions are declared in ``include/WuxSdyExt.h``,
and the containing directory is added to ``wux.includes``.

The ``lib/WuxSdyProxy.cpp`` resource file is required and is added to
``wux.sources``.

SCADE Suite UA Adaptor Extension (``WUX2_UUA``)
-----------------------------------------------

This service is responsible for generating the DF files for each A661 panel
referenced in the configuration, running SCADE UA Adaptor for the root
operators, and providing functions to send/receive A661 messages at runtime.

It generates the following functions in ``wuxuaa<project name>.c``:

* ``int WuxA661ConnectServer()``: Connect to the A661 server,
  and returns 0 on success.
* ``int WuxA661DisconnectServer()``: Disconnect from the A661 server,
  and returns 0 on success.
* ``void WuxA661ReceiveMessages()``: Receive the A661 messages,
  and copy the mapped values to the contexts.
* ``void WuxA661SendMessages()``: Get the mapped values form the contexts,
  and send all the A661 messages.

The generated file as well as the files generated by SCADE UA Adaptor are
added to `wux.sources`.

.. Note:
  The functions are always generated to avoid link errors,
  but are empty if no graphical panel is referenced in the configuration.

All the generated functions are declared in ``include/WuxA661Ext.h``,
and the containing directory is added to ``wux.includes``.

The ``lib/A661Connect.c`` resource file is required and is added to
``wux.sources``.

Extension for Integration's/ Simulator's extensions (``WUX2_SIMU_EXT``)
-----------------------------------------------------------------------

.. Note:
  This generation service has been initially designed to allow the
  usage of SCADE Simulator with one or more wrappers together with
  SCADE graphical panels.
  It has then been extended to provide a generic way of integrating extensions
  with the Wrapper ``Generic Integration`` described in the next section.
  It has not been renamed for compatibility reasons.
  The following text describes the connection to the SCADE Simulator but this
  applies to any host.

This generation service does not generate new files, but provides a workaround
for a limitation of the SCADE Simulator interface. Indeed, the SCADE Simulator
allows hooks thanks to functions like ``BeforeSimInit``, ``BeforeSimStep``,
``AfterSimStep``, etc. when the preprocessor variable ``EXTENDED_SIM`` is
defined. This allows wrapping code, for example with communications to
external environments, to be executed in the SCADE Simulator without requiring
imported operators for the I/Os.

Unfortunately, if the wrapping code is used together with graphical panels,
the existing hook mechanism is not enough: Two different pieces of code define
the same functions and this leads to link errors.

The purpose of this generation service is to patch the file
``<project name>_interface.c`` generated by the Simulator Wrapper so that:

* The file includes ``WuxSimuExt.h``.
* ``EXTENDED_SIM`` is always defined in this file.
* All the calls to a ``Xxx`` hook function is replaced by a call to the
  ``WuxXxx`` function.

The ``WuxXxx`` functions are declared in ``include/WuxSimuExt.h`` and the
containing directory is added to ``wux.includes``. They are implemented in
the ``lib/WuxSimuExt.cpp`` resource file that is required, and added to
``wux.sources``. The implementation consists in calling the function for
each registered extension.

The wrappers that want to hook the SCADE Simulator, or to be compatible with
the wrapper ``Integration``, must create a static instance of a class deriving
from ``CWuxSimulatorExtension``:

.. code-block:: c++

  class CWuxSimulatorExtension
  {
  public:
      CWuxSimulatorExtension();
      virtual ~CWuxSimulatorExtension();
      // simulator interface
      virtual void BeforeSimInit();
      virtual void AfterSimInit();
      virtual void BeforeSimStep();
      virtual void AfterSimStep();
      virtual void ExtendedSimStop();
      virtual void ExtendedGatherDumpData(char* pData);
      virtual void ExtendedRestoreDumpData(const char* pData);
      virtual int ExtendedGetDumpSize();
      virtual void UpdateValues();
      virtual void UpdateSimulatorValues();
      // integration interface
      virtual const char* GetIdent();
      virtual bool IntegrationStart(int argc, char* argv[]);
      virtual void IntegrationStop();
      virtual bool SelfPaced();
      virtual bool IsAlive();
      // misc.
      virtual void Logf(int nLevel, const char* pszFormat, ...);
  };

* The constructor automatically registers the instance to the list of hooks.
  All the functions have an empty implementation by default.
* The functions listed in the ``integration interface`` section are not used
  in the context of the SCADE Simulator.
* When ``EXTENDED_SIM`` is defined, the source defines a specific instance of
  ``CWuxSimulatorExtension`` that calls the former global hooks to ensure the
  compatibility with the existing services, especially the simulation with
  graphical panels.

The example hereafter shows the usage of this feature for the wrapper Connext-DDS:

.. code-block:: c++

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
  Vive versa for the ``_WriteData()`` function.
* The initialization/termination of the external environment has no more to be
  done in ``DllMain``, which often lead to thread issues.

This design allows using graphical panels in the Simulation... or not.

.. Note:
  All target wrappers embedding these extensions must define the preprocessor
  directive ``WUX_STANDALONE``. In other words, the macro ``WUX_STANDALONE``
  is not defined if and only if the extension is used in the context of the
  SCADE Simulator.

Extension for DllMain (``WUX2_DLL_EXT``)
----------------------------------------

This generation service does not generate new files, but allows several
services to subscribe to ``DllMain``.

A wrapper which needs an access to ``DllMain`` must include ``WuxDllExt.h``
and define a static instance of a class deriving from ``CWuxDllInstance``:

.. code-block:: c++

  class CWuxDllInstance
  {
  public:
      CWuxDllInstance();
      virtual ~CWuxDllInstance();
      // interface
      virtual BOOL OnProcessAttach(HMODULE htDllInstance);
      virtual BOOL OnThreadAttach(HMODULE htDllInstance);
      virtual BOOL OnThreadDetach(HMODULE htDllInstance);
      virtual BOOL OnProcessDetach(HMODULE htDllInstance);
  };

* The constructor automatically registers the instance to the list of hooks.
* All the functions have an empty implementation by default.

The directory containing ``WuxSimuExt.h`` is added to ``wux.includes``.

The ``lib/WuxDllExt.cpp`` resource file is added to ``wux.sources``.
