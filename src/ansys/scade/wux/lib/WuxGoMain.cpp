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

// Runtime for combined SCADE Suite integrations
// WUX_STANDALONE is defined when the target is not the SCADE Simulator

#ifdef _WIN32
#include <Windows.h>
#else
#include <string.h>
#endif
#include <stdlib.h>
#include <stdio.h>
#include <time.h>

#include "WuxCtxExt.h"
#ifdef _WIN32
#include "WuxSdyProxy.h"
#include "WuxSdyExt.h"
#include "WuxA661Ext.h"
#endif
#include "WuxSimuExt.h"

int main(int argc, char *argv[])
{
    // nLatency used iff one extension is self paced
    int nLatency = 0;
    int nCount = WuxGetExtensionsCount();
    CWuxSimulatorExtension** extensions = WuxGetExtensions();

    for (int i = 0; i < argc; i++) {
        if (!strcmp(argv[i], "-latency")) {
            nLatency = atoi(argv[++i]);
        }
    }

    bool bSelfPaced = false;
    for (int i = 0; i < nCount; i++) {
        CWuxSimulatorExtension* extension = extensions[i];
        bool status = extension->IntegrationStart(argc, argv);
        if (!status) {
            printf("failed to initialize %s: exiting\n", extension->GetIdent());
            return 1;
        }
        bSelfPaced |= extension->SelfPaced();
    }

#ifdef _WIN32
    if (!WuxLoadSdyDlls(GetModuleHandle(NULL))) {
        printf("failed to initialize graphical panels: exiting\n");
        return 2;
    }

    bool bServerStarted = WuxA661ConnectServer();
#endif

    // extensions
    WuxBeforeSimInit();

    WuxInit();
    WuxReset();
#ifdef _WIN32
    WuxSdyInit();
    WuxSdyDraw();
#endif

    // extensions
    WuxAfterSimInit();

    // main loop
    int nDelay = !bSelfPaced ? (int)(1000. * WuxGetPeriod()) : nLatency;
    while (true) {
        clock_t start = clock();

#ifdef _WIN32
        if (WuxSdyCancelled()) {
            break;
        }
#endif

        bool bStop = false;
        for (int i = 0; i < nCount && !bStop; i++) {
            CWuxSimulatorExtension* extension = extensions[i];
            if (!extension->IsAlive()) {
                printf("extension terminated %s: exiting\n", extension->GetIdent());
                bStop = true;
            }
        }
        if (bStop) {
            break;
        }

        // extensions
        WuxBeforeSimStep();

#ifdef _WIN32
        WuxA661ReceiveMessages();
#endif

        // call the module (Logic + Displays)
        WuxCycle();
#ifdef _WIN32
        WuxSdySetInputs();
        WuxSdyDraw();

        WuxA661SendMessages();
        WuxSdyGetOutputs();
#endif

        // extensions
        WuxAfterSimStep();

        clock_t finish = clock();
        if (nDelay != 0) {
#ifdef _MSC_VER
            // sleep if the delay is not null
            int duration = (int)(((double)(finish - start)) / CLOCKS_PER_SEC * 1000);
            Sleep(duration >= nDelay ? 1 : nDelay - duration);
#else
            // TODO gcc
#endif
        }
    }

    // extensions
    WuxExtendedSimStop();

#ifdef _WIN32
    WuxUnloadSdyDlls(NULL);

    if (bServerStarted) {
        WuxA661DisconnectServer();
    }
#endif

    for (int i = 0; i < nCount; i++) {
        CWuxSimulatorExtension* extension = extensions[i];
        extension->IntegrationStop();
    }

    return 0;
}
