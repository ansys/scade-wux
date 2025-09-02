# Integration test for C/C++ Simulation Hooks
## Overview
The project `Hooks` allows testing manually the C/C++ Simulation Hooks extension.

## Setup
* Register the package to SCADE as detailed in
  [Install in user mode](<https://wux.scade.docs.pyansys.com/version/dev/contributing.html#install-in-user-mode>).

## Test
* Select the configuration `UT Simulation` for SCADE 2025 R1 or greater, otherwise the configuration `UT Simulation 24R2`.
* Launch the command `Project/Code Generator/Rebuild All Node Root` and verify the build is successful.
* Launch the command `Project/Code Generator/Run Node Root`.
* Perform few steps with different input values and verify the sensor's value is the input's value from the previous cycle.
* Launch the command `Simulation/Stop`.

## Clean
You may uninstall the package once the tests are completed:

* Unregister the package from SCADE as detailed in
  [Uninstall](<https://wux.scade.docs.pyansys.com/version/dev/contributing.html#uninstall>).
