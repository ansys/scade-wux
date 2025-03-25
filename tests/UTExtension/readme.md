# Integration test for an extension
## Overview
The project `UTExtension` allows testing the Generic Integration wrapper and the following generation services:

* WUX2_CTX
* WUX2_SIMU_EXT

It consists of a code generation extension that logs the available callbacks and illustrates how to generate C code.

The test is automated for environments based on Python 3.12, or greater, and Ansys SCADE starting 2026 R1.
The next sections describe the manual test procedure for Ansys SCADE up to 2025 R2.

## Setup
* Register the package to SCADE as detailed in
  [Install in user mode](<https://wux.scade.docs.pyansys.com/version/dev/contributing.html#install-in-user-mode>).
* Register the test extension to SCADE: Run the PowerShell script
  `Extension\reggitext.ps1`, from its directory.
  A right click *Run with PowerShell* in the explorer window is easier.

  This commands copies `Extension\wux_ut_ext.srg` to `%APPDATA%\SCADE\Customize` and updates it according to your working directory.

## Test
### Command line
* Open `Model/Model.etp` with SCADE Suite.
* Select the configuration `Integration`.
* Launch the command `Project/Code Generator/Rebuild All Node Root` and verify the build is successful.
* Open a command line window and execute the executable produced in the previous step:

  ```cmd
  Model\Integration\P_Root.exe
  ```

  Verify it displays traces as follows:

  ```
  INFO: IntegrationStart() with 1 parameters
  INFO: SelfPaced()
  INFO: BeforeSimInit()
  INFO: AfterSimInit()
  INFO: IsAlive()
  INFO: BeforeSimStep(1)
  INFO: AfterSimStep(1)
  INFO: last = 1
  INFO: IsAlive()
  INFO: BeforeSimStep(2)
  INFO: AfterSimStep(2)
  INFO: last = 2
  ...
  INFO: BeforeSimStep(5)
  INFO: AfterSimStep(5)
  INFO: last = 5
  INFO: IsAlive()
  INFO: last = 6
  ...
  INFO: IsAlive()
  INFO: last = 10
  INFO: IsAlive()
  extension terminated WUX Unit Test Extension: exiting
  INFO: ExtendedSimStop()
  INFO: IntegrationStop()
  ```

### Simulation
* Open `Model/Model.etp` with SCADE Suite.
* Select the configuration `Simulation`.
* Launch the command `Project/Code Generator/Rebuild All Node Root` and verify the build is successful.
* Launch the command `Project/Code Generator/Run Node Root` to start a SCADE Simulator session.
  * Perform a few steps and verify the input of a step is the output of the previous one
  * Verify you have traces in the `Simulator` tab of the `Output` window, as follows:

    ```
    BeforeSimInit()
    AfterSimInit()
    BeforeSimStep(1)
    AfterSimStep(1)
    last = 1
    BeforeSimStep(2)
    AfterSimStep(2)
    last = 2
    BeforeSimStep(3)
    AfterSimStep(3)
    last = 3
    BeforeSimStep(4)
    AfterSimStep(4)
    last = 4
    ...
    ```

## Clean
You may uninstall the package once the tests are completed:

* Unregister the package from SCADE as detailed in
  [Uninstall](<https://wux.scade.docs.pyansys.com/version/dev/contributing.html#uninstall>).
* Unregister the test extension:

  ```cmd
  del %APPDATA%\SCADE\Customize\wux_ut_ext.srg
  ```
