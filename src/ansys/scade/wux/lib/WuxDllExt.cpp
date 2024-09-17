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

// SCADE Suite DllInstance management

#ifdef _WIN32
#include <Windows.h>
#include "WuxDllExt.h"

// ---------------------------------------------------------------------------
// extension interface and registration
// ---------------------------------------------------------------------------

#define MAX_DLL_INSTANCES 256

static int _nDllInstancesCount;
static CWuxDllInstance* _dllInstances[MAX_DLL_INSTANCES];

int WuxGetDllInstancesCount()
{
    return _nDllInstancesCount;
}

CWuxDllInstance** WuxGetDllInstances()
{
    return _dllInstances;
}

static void RegisterDllInstance(CWuxDllInstance* pDllInstance)
{
    if (_nDllInstancesCount < MAX_DLL_INSTANCES) {
        _dllInstances[_nDllInstancesCount++] = pDllInstance;
    }
}

CWuxDllInstance::CWuxDllInstance()
{
    RegisterDllInstance(this);
}

CWuxDllInstance::~CWuxDllInstance()
{
}

BOOL CWuxDllInstance::OnProcessAttach(HMODULE hDllInstance)
{
    return TRUE;
}

BOOL CWuxDllInstance::OnThreadAttach(HMODULE hDllInstance)
{
    return TRUE;
}

BOOL CWuxDllInstance::OnThreadDetach(HMODULE hDllInstance)
{
    return TRUE;
}

BOOL CWuxDllInstance::OnProcessDetach(HMODULE hDllInstance)
{
    return TRUE;
}

static HMODULE _hDllInstance;

HMODULE WuxGetDllInstance()
{
    return _hDllInstance;
}

BOOL APIENTRY DllMain(HMODULE hModule,
    DWORD  ul_reason_for_call,
    LPVOID lpReserved
)
{
    BOOL bResult = TRUE;

    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
        _hDllInstance = hModule;
        for (int i = 0; i < _nDllInstancesCount; i++) {
            bResult &= _dllInstances[i]->OnProcessAttach(_hDllInstance);
        }
        break;
    case DLL_THREAD_ATTACH:
        for (int i = 0; i < _nDllInstancesCount; i++) {
            bResult &= _dllInstances[i]->OnThreadAttach(_hDllInstance);
        }
        break;
    case DLL_THREAD_DETACH:
        for (int i = 0; i < _nDllInstancesCount; i++) {
            bResult &= _dllInstances[i]->OnThreadDetach(_hDllInstance);
        }
        break;
    case DLL_PROCESS_DETACH:
        for (int i = 0; i < _nDllInstancesCount; i++) {
            bResult &= _dllInstances[i]->OnProcessDetach(_hDllInstance);
        }
        break;
    }
    return bResult;
}
#endif // _WIN32

// ---------------------------------------------------------------------------
//end of file
// ---------------------------------------------------------------------------
