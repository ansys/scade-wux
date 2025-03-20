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

// WUX2 Unit Test extension

#include <string.h>
#include <stdlib.h>
#include <stdarg.h>

#include "WuxSimuExt.h"

#include "WuxUTExt.h"

static class CWuxUTExtension : public CWuxSimulatorExtension
{
public:
    CWuxUTExtension()
    : m_nStep(0), m_nMaxSteps(10), m_nMaxLoggedSteps(5)
    {
    }

    // SCADE Simulator callbacks
    void BeforeSimInit() {
        WuxLogf(SIM_INFO, "BeforeSimInit()");
        // reset the current step
        m_nStep = 0;
    }

    void AfterSimInit() {
        WuxLogf(SIM_INFO, "AfterSimInit()");

        // reset the state of the generated code
        WuxUTExtReset();
    }

    void BeforeSimStep()
    {
        m_nStep++;
        if (m_nStep <= m_nMaxLoggedSteps) {
            WuxLogf(SIM_INFO, "BeforeSimStep(%d)", m_nStep);
        }

        // set the inputs of the root operators
        WuxUTExtSetInputs();
    }

    void AfterSimStep()
    {
        if (m_nStep <= m_nMaxLoggedSteps) {
            WuxLogf(SIM_INFO, "AfterSimStep(%d)", m_nStep);
        }

        // do something with the inputs of the root operators
        WuxUTExtGetOutputs();    }

    void ExtendedSimStop()
    {
        WuxLogf(SIM_INFO, "ExtendedSimStop()");
    }

    void ExtendedGatherDumpData(char* pData)
    {
        WuxLogf(SIM_INFO, "ExtendedGatherDumpData(pData)");
    }

    void ExtendedRestoreDumpData(const char* pData)
    {
        WuxLogf(SIM_INFO, "ExtendedRestoreDumpData()");
    }

    int ExtendedGetDumpSize()
    {
        WuxLogf(SIM_INFO, "ExtendedGetDumpSize()");
        return 0;
    }

    void UpdateValues()
    {
        WuxLogf(SIM_INFO, "UpdateValues()");
    }

    void UpdateSimulatorValues()
    {
        WuxLogf(SIM_INFO, "UpdateSimulatorValues()");
    }

    // generic integration interface
    const char* GetIdent()
    {
        return "WUX Unit Test Extension";
    }

    bool IntegrationStart(int argc, char* argv[])
    {
        WuxLogf(SIM_INFO, "IntegrationStart() with %d parameters", argc);

        // update the default of m_nMaxSteps
        for (int i = 0; i < argc; i++) {
            if (!strcmp(argv[i], "-max_steps")) {
                if (i == argc - 1) {
                    WuxLogf(SIM_ERROR, "no value specified for -max_steps");
                    return false;
                }
                else {
                    i++;
                    WuxLogf(SIM_INFO, "set max steps steps to %s", argv[i]);
                    m_nMaxSteps = atoi(argv[i]);
                }
            }
            else if (!strcmp(argv[i], "-max_log")) {
                if (i == argc - 1) {
                    WuxLogf(SIM_ERROR, "no value specified for -max_log");
                    return false;
                }
                else {
                    i++;
                    WuxLogf(SIM_INFO, "set max logged steps to %s", argv[i]);
                    m_nMaxLoggedSteps = atoi(argv[i]);
                }
            }
        }
        return true;
    }

    void IntegrationStop()
    {
        WuxLogf(SIM_INFO, "IntegrationStop()");
    }

    bool SelfPaced()
    {
        WuxLogf(SIM_INFO, "SelfPaced()");
        return false;
    }

    bool IsAlive()
    {
        WuxLogf(SIM_INFO, "IsAlive()");
        return m_nStep < m_nMaxSteps;
    }

protected:
    // maximum number of stepd to be logged
    int m_nMaxLoggedSteps;
    // maximum number of steps to be executed (standalone executable only)
    int m_nMaxSteps;
    // current step
    int m_nStep;
} wuxUTExtension;
