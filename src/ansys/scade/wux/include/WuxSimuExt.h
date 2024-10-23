/*
 * Copyright (C) 2020 - 2024 ANSYS, Inc. and/or its affiliates.
 * SPDX-License-Identifier: MIT
 *
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

#ifndef _WUX_SIMU_EXT_H_88D3C7D0_032B_4F14_A265_7950453CC8D1_
#define _WUX_SIMU_EXT_H_88D3C7D0_032B_4F14_A265_7950453CC8D1_

/**
 * @file
 * @brief Interfaces for standalone executables or simulation DLL extensions.
 *
 */

#ifdef __cplusplus
extern "C" {
#endif

//{{ definitions from xxx_interface.h: no easy way to include this generated file from the runtime
/**
 * @brief "Information" level for WuxLogf
 *
 */
#define SIM_INFO    1
 /**
  * @brief "Warning" level for WuxLogf
  *
  */
#define SIM_WARNING 2
  /**
   * @brief "Error" level for WuxLogf
   *
   */
#define SIM_ERROR   3

#ifndef NO_DOXYGEN
#ifndef WUX_STANDALONE
extern void SsmOutputMessage(int level, const char* str);
#endif
#endif /* NO_DOXYGEN */
//}}

/**
 * @brief Log a message.
 *
 * The message is logged to the standard output, or to the *Simulator* tab
 * of the output window when the target is the SCADE Simulator.
 *
 * @param nLevel SIM_INFO, SIM_WARNING or SIM_ERROR
 * @param pszFormat Format control
 * @param ... Optional arguments
 */
void WuxLogf(int nLevel, const char* pszFormat, ...);

 /* ---------------------------------------------------------------------------
  * C interface for the simulator
  * ------------------------------------------------------------------------ */

#ifndef NO_DOXYGEN
extern void WuxBeforeSimInit();
extern void WuxAfterSimInit();
extern void WuxBeforeSimStep();
extern void WuxAfterSimStep();
extern void WuxExtendedSimStop();
extern void WuxExtendedGatherDumpData(char* pData);
extern void WuxExtendedRestoreDumpData(const char* pData);
extern int WuxExtendedGetDumpSize();
extern void WuxUpdateValues();
extern void WuxUpdateSimulatorValues();

/* defined in xxx_interface.c */
extern int GraphicalInputsConnected;
#endif /* NO_DOXYGEN */

#ifdef __cplusplus
}
#endif

#ifdef __cplusplus
/* ---------------------------------------------------------------------------
 * extension interface and registration
 * ------------------------------------------------------------------------ */

 /**
  * @brief Base class for extending a standalone executable or a SCADE
  * simulation DLL.
  *
  * This class provides two interfaces:
  *
  * * Callbacks for the integrating application, for example the
  *   SCADE Simulator or the *Generic Integration* wrapper's standalone
  *   executable.
  * * Extended callbacks for integration applications other than the
  *   SCADE Simulator.
  *
  */
class CWuxSimulatorExtension
{
public:
    /**
     * @brief Construct the instance and registers it.
     *
     */
    CWuxSimulatorExtension();
    /**
     * @brief Unregister the instance.
     */
    virtual ~CWuxSimulatorExtension();

    // simulator interface
    /**
     * @brief Process the notification ``BeforeSimInit``.
     *
     * This notification is sent before the initialization of the generated
     * code, either from SCADE Suite or from SCADE Display.
     *
     * The default implementation is empty.
     */
    virtual void BeforeSimInit();
    /**
     * @brief Process the notification ``AfterSimInit``.
     *
     * This notification is sent after the initialization of the generated
     * code, either from SCADE Suite or from SCADE Display.
     *
     * The default implementation is empty.
     */
    virtual void AfterSimInit();
    /**
     * @brief Process the notification ``BeforeSimStep``.
     *
     * This notification is sent before the call to the cyclic function
     * of the root operators.
     *
     * The default implementation is empty.
     */
    virtual void BeforeSimStep();
    /**
     * @brief Process the notification ``AfterSimStep``.
     *
     * This notification is sent after the call to the cyclic function
     * of the root operators.
     *
     * The default implementation is empty.
     */
    virtual void AfterSimStep();
    /**
     * @brief Process the notification ``ExtendedSimStop``.
     *
     * This notification is sent when the main loop exits.
     *
     * The default implementation is empty.
     */
    virtual void ExtendedSimStop();
    /**
     * @brief Retrieve additional dump data.
     *
     * This function is called by the SCADE Simulator and its
     * purpose is unclear.
     *
     * The default implementation is empty.
     */
    virtual void ExtendedGatherDumpData(char* pData);
    /**
     * @brief Restore additional dump data.
     *
     * This function is called by the SCADE Simulator and its
     * purpose is unclear.
     *
     * The default implementation is empty.
     */
    virtual void ExtendedRestoreDumpData(const char* pData);
    /**
     * @brief Return the size of additional dump data.
     *
     * This function is called by the SCADE Simulator and its
     * purpose is unclear.
     *
     * The default implementation returns 0.
     */
    virtual int ExtendedGetDumpSize();
    /**
     * @brief Process the notification ``UpdateValues``.
     *
     * This function is called by the SCADE Simulator and its
     * purpose is unclear.
     *
     * The default implementation is empty.
     */
    virtual void UpdateValues();
    /**
     * @brief Process the notification ``UpdateSimulatorValues``.
     *
     * This function is called by the SCADE Simulator and its
     * purpose is unclear.
     *
     * The default implementation is empty.
     */
    virtual void UpdateSimulatorValues();

    // integration interface
    /**
     * @brief Return the identifier of the extension.
     *
     * The default implementation returns ``"<none>"``.
     * @return const char*
     */
    virtual const char* GetIdent();
    /**
     * @brief Process the notification ``IntegrationStart``.
     *
     * This function is called at startup, when the target is not the
     * SCADE Simulator. It allows accessing the command line parameters
     * specified when running the standalone executable.
     *
     * Return ``false`` to stop the process, otherwise ``true``.
     *
     * The default implementation is empty and returns ``true``.
     *
     * @param argc number of parameters
     * @param argv array of parameters
     * @ return bool
     */
    virtual bool IntegrationStart(int argc, char* argv[]);
    /**
     * @brief Process the notification ``IntegrationStop``.
     *
     * This function is called before the process stops, when the target is
     * not the SCADE Simulator.
     *
     * The default implementation is empty.
     */
    virtual void IntegrationStop();
    /**
     * @brief Return whether the extension has its own synchronization mechanism.
     *
     * When none of the registered extensions returns ``true``, the integration
     * uses the specified period to clock the main loop.
     *
     * This function is not called when the target is the SCADE Simulator.
     *
     * The default implementation returns ``false``.
     */
    virtual bool SelfPaced();
    /**
     * @brief Return whether the extension is alive.
     *
     * The process stops as soon as a registered extension returns ``false``.
     * For example, when a connection is closed.
     *
     * This function is not called when the target is the SCADE Simulator.
     *
     * The default implementation returns ``true``.
     */
    virtual bool IsAlive();
};

// access to the registered extensions
/**
 * @brief Return the number of registered extensions.
 * @return int
 */
int WuxGetExtensionsCount();
/**
 * @brief Return the array of the registered extensions.
 *
 * The number of elements is provided by ``WuxGetExtensionsCount``.
 * @return CWuxSimulatorExtension**
 */
CWuxSimulatorExtension** WuxGetExtensions();

#endif /* __cplusplus */

#endif /* _WUX_SIMU_EXT_H_88D3C7D0_032B_4F14_A265_7950453CC8D1_ */
