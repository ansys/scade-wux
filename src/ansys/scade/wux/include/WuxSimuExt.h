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

#ifdef __cplusplus
extern "C" {
#endif

//{{ definitions from xxx_interface.h: no easy way to include this generated file from the runtime
#define SIM_INFO    1
#define SIM_WARNING 2
#define SIM_ERROR   3
#ifndef WUX_STANDALONE
extern void SsmOutputMessage(int level, const char* str);
#endif
//}}

 /* ---------------------------------------------------------------------------
  * C interface for the simulator
  * ------------------------------------------------------------------------ */

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

#ifdef __cplusplus
}
#endif

#ifdef __cplusplus
/* ---------------------------------------------------------------------------
 * extension interface and registration
 * ------------------------------------------------------------------------ */

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
    virtual void Logf(int nLevel, const char* pszFormat, ...);
};

// access to the registered extensions
int WuxGetExtensionsCount();
CWuxSimulatorExtension** WuxGetExtensions();

#endif /* __cplusplus */

#endif /* _WUX_SIMU_EXT_H_88D3C7D0_032B_4F14_A265_7950453CC8D1_ */
