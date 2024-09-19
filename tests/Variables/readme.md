# Integration test for SCADE Display
## Overview
The project variables allows testing manually the Generic Integration wrapper and the following generation services:

* WUX2_SDY
* WUX2_SIMU_EXT

## Setup
Register the package to SCADE:

```cmd
<python310.exe> -m pip install --user --editable .
```

You can reuse any `<SCADE Installation dir>\SCADE\contrib\Python310\python.exe` or Python 3.10 installation on your computer.

If you are using SCADE 2024 R2 or below, register the package to SCADE:

```cmd
<python310.exe> -m ansys.scade.wux.register
```

## Test
* Select the configuration `SdyExt` for SCADE 2025 R1 or greater, otherwise the configuration `SdyExt 24R2`.
* Launch the command `Project/Code Generator/Rebuild All Node Engine` and verify the build is successful.
* Launch the command `Project/Code Generator/Run Node Engine` and verify a small  window pops up with two counters.
* Close the window and verify the command `Project/Code Generator/Stop` is no longer available.


## Cleaning
You may uninstall the package once the tests are completed:

```cmd
<python3.10.exe> -m pip uninstall ansys-scade-wux
```

If you are using SCADE 2024 R2 or below, remove the SCADE registration:

```cmd
del %APPDATA%\SCADE\Customize\wux24r2.srg
```
