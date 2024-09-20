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

// SCADE Suite Simulator extensions management

#include <stdio.h>
#include <stdarg.h>
#include <string.h>

#include "WuxSimuExt.h"

// ---------------------------------------------------------------------------
// extension interface and registration
// ---------------------------------------------------------------------------

#define MAX_SIMULATOR_EXTENSIONS 256

static int _nSimulatorExtensionsCount;
static CWuxSimulatorExtension* _simulatorExtensions[MAX_SIMULATOR_EXTENSIONS];
static int _nExtendedDumpDataSizes[MAX_SIMULATOR_EXTENSIONS];

int WuxGetExtensionsCount()
{
    return _nSimulatorExtensionsCount;
}

CWuxSimulatorExtension** WuxGetExtensions()
{
    return _simulatorExtensions;
}

static void RegisterSimulatorExtension(CWuxSimulatorExtension* pExtension)
{
    if (_nSimulatorExtensionsCount < MAX_SIMULATOR_EXTENSIONS) {
        _simulatorExtensions[_nSimulatorExtensionsCount++] = pExtension;
    }
}

CWuxSimulatorExtension::CWuxSimulatorExtension()
{
    RegisterSimulatorExtension(this);
}

CWuxSimulatorExtension::~CWuxSimulatorExtension()
{
}

// simulator interface
void CWuxSimulatorExtension::BeforeSimInit()
{
}

void CWuxSimulatorExtension::AfterSimInit()
{
}

void CWuxSimulatorExtension::BeforeSimStep()
{
}

void CWuxSimulatorExtension::AfterSimStep()
{
}

void CWuxSimulatorExtension::ExtendedSimStop()
{
}

void CWuxSimulatorExtension::ExtendedGatherDumpData(char* pData)
{
}

void CWuxSimulatorExtension::ExtendedRestoreDumpData(const char* pData)
{
}

int  CWuxSimulatorExtension::ExtendedGetDumpSize()
{
    return 0;
}

void CWuxSimulatorExtension::UpdateValues()
{
}

void CWuxSimulatorExtension::UpdateSimulatorValues()
{
}

// integration interface
const char* CWuxSimulatorExtension::GetIdent()
{
    return "<none>";
}

bool CWuxSimulatorExtension::IntegrationStart(int argc, char* argv[])
{
    return true;
}

void CWuxSimulatorExtension::IntegrationStop()
{
}

bool CWuxSimulatorExtension::SelfPaced()
{
    return false;
}

bool CWuxSimulatorExtension::IsAlive()
{
    return true;
}

// logging
void WuxLogf(int nLevel, const char* pszFormat, ...)
{
    va_list args;
    va_start(args, pszFormat);

    int nSize = _vscprintf(pszFormat, args) + 1; // Extra space for '\0'
    if (nSize <= 1) {
        // error during formatting
        return;
    }
    char* buf = new char[nSize];
#ifdef _MSC_VER
    vsprintf_s(buf, nSize, pszFormat, args);
#else
    vsprintf(buf, pszFormat, args);
#endif
#ifndef WUX_STANDALONE
    int l = (int) strlen(buf) - 1;
    if (l > 0 && buf[l] == '\n') {
        // remove trailing \n since SsmOutputMsg adds one
        buf[l] = '\0';
    }
    SsmOutputMessage(nLevel, buf);
#else
    switch (nLevel) {
    case SIM_INFO:
        printf("INFO: ");
        break;
    case SIM_WARNING:
        printf("WARNING: ");
        break;
    case SIM_ERROR:
        printf("ERROR: ");
        break;
    }
    printf("%s\n", buf);
#endif
    delete[] buf;

    va_end(args);
}

// ---------------------------------------------------------------------------
// C interface for the simulator
// ---------------------------------------------------------------------------

void WuxBeforeSimInit()
{
    for (int i = 0; i < _nSimulatorExtensionsCount; i++) {
        _simulatorExtensions[i]->BeforeSimInit();
    }
}

void WuxAfterSimInit()
{
    for (int i = 0; i < _nSimulatorExtensionsCount; i++) {
        _simulatorExtensions[i]->AfterSimInit();
    }
}

void WuxBeforeSimStep()
{
    for (int i = 0; i < _nSimulatorExtensionsCount; i++) {
        _simulatorExtensions[i]->BeforeSimStep();
    }
}

void WuxAfterSimStep()
{
    for (int i = 0; i < _nSimulatorExtensionsCount; i++) {
        _simulatorExtensions[i]->AfterSimStep();
    }
}

void WuxExtendedSimStop()
{
    for (int i = 0; i < _nSimulatorExtensionsCount; i++) {
        _simulatorExtensions[i]->ExtendedSimStop();
    }
}

void WuxExtendedGatherDumpData(char* pData)
{
    int nOffset = 0;
    for (int i = 0; i < _nSimulatorExtensionsCount; i++) {
        _simulatorExtensions[i]->ExtendedGatherDumpData(pData);
        nOffset += _nExtendedDumpDataSizes[i];
    }
}

void WuxExtendedRestoreDumpData(const char* pData)
{
    int nOffset = 0;
    for (int i = 0; i < _nSimulatorExtensionsCount; i++) {
        _simulatorExtensions[i]->ExtendedRestoreDumpData(pData + nOffset);
        nOffset += _nExtendedDumpDataSizes[i];
    }
}

int WuxExtendedGetDumpSize()
{
    int nSize = 0;
    for (int i = 0; i < _nSimulatorExtensionsCount; i++) {
        _nExtendedDumpDataSizes[i] = _simulatorExtensions[i]->ExtendedGetDumpSize();
        nSize += _nExtendedDumpDataSizes[i];
    }
    return nSize;
}

void WuxUpdateValues()
{
    for (int i = 0; i < _nSimulatorExtensionsCount; i++) {
        _simulatorExtensions[i]->UpdateValues();
    }
}

void WuxUpdateSimulatorValues()
{
    for (int i = 0; i < _nSimulatorExtensionsCount; i++) {
        _simulatorExtensions[i]->UpdateSimulatorValues();
    }
}

#ifdef EXTENDED_SIM
// ---------------------------------------------------------------------------
// redeclaration of the functions defined in xxx_interface.h
// ---------------------------------------------------------------------------

extern "C" {
    extern void BeforeSimInit();
    extern void AfterSimInit();
    extern void BeforeSimStep();
    extern void AfterSimStep();
    extern void ExtendedSimStop();
    extern void ExtendedGatherDumpData(char* pData);
    extern void ExtendedRestoreDumpData(const char* pData);
    extern int  ExtendedGetDumpSize();
    extern void UpdateValues();
    extern void UpdateSimulatorValues();
}

// ---------------------------------------------------------------------------
// backward compatibility, for SCADE Display or other extensions
// ---------------------------------------------------------------------------

static class CWuxExtendedSimulatorExtension : public CWuxSimulatorExtension
{
    void BeforeSimInit() {
        ::BeforeSimInit();
    }

    void AfterSimInit() {
        ::AfterSimInit();
    }

    void BeforeSimStep()
    {
        ::BeforeSimStep();
    }

    void AfterSimStep()
    {
        ::AfterSimStep();
    }

    void ExtendedSimStop()
    {
        ::ExtendedSimStop();
    }

    void ExtendedGatherDumpData(char* pData)
    {
        ::ExtendedGatherDumpData(pData);
    }

    void ExtendedRestoreDumpData(const char* pData)
    {
        ::ExtendedRestoreDumpData(pData);
    }

    int ExtendedGetDumpSize()
    {
        return ::ExtendedGetDumpSize();
    }

    void UpdateValues()
    {
        ::UpdateValues();
    }

    void UpdateSimulatorValues()
    {
        ::UpdateSimulatorValues();
    }
} extendedSimulatorExtension;
#endif /* EXTENDED_SIM */
