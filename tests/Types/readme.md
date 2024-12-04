# Integration test for SCADE Display
## Overview
The project `Types` allows testing manually the Generic Integration wrapper and the following generation services:

* WUX2_CTX
* WUX2_SDY
* WUX2_SDY_PROXY

## Setup
* Register the package to SCADE as detailed in
  [Install in user mode](<https://wux.scade.docs.pyansys.com/version/dev/contributing.html#install-in-user-mode>).

## Test
* Select the configuration `SdyExt` for SCADE 2025 R1 or greater, otherwise the configuration `SdyExt 24R2`.
* Launch the command `Project/Code Generator/Rebuild All Nodes` and verify the build is successful.
* Launch the command `Project/Code Generator/Run Nodes` and verify a small window pops up with a green circle.
* Close the window and verify the command `Project/Code Generator/Stop` is no longer available.

## Clean
You may uninstall the package once the tests are completed:

* Unregister the package from SCADE as detailed in
  [Uninstall](<https://wux.scade.docs.pyansys.com/version/dev/contributing.html#uninstall>).
