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

// Proxy for SCADE Display DLL

#ifdef _WIN32
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>

#include "sdy/sdy_events.h"

#include "WuxSdyExt.h"
#include "WuxSdyDll.h"

CSdyDllProxy::CSdyDllProxy()
    : m_hDll(NULL)
{
    ZeroPointers();
}

CSdyDllProxy::~CSdyDllProxy()
{
    Unload();
}

void CSdyDllProxy::ZeroPointers()
{
#define SDY_PROC(RETURN,PREFIX,NAME,SIG,ARGS) \
    m_pfn##NAME = NULL;

    SDY_SIGNATURES(UNUSED)
#undef SDY_PROC
}

BOOL CSdyDllProxy::Load(HINSTANCE hinstDll, const char* pszBasename)
{
    char szBuffer[MAX_PATH];
    char szDrive[MAX_PATH];
    char szDir[MAX_PATH];
    char szName[MAX_PATH];
    char szExt[MAX_PATH];

    if (!Unload()) {
	return FALSE;
    }

    // search for the DLL in the same directory
    GetModuleFileNameA((HINSTANCE) hinstDll, szBuffer, sizeof(szBuffer));
    _splitpath_s<sizeof(szDrive), sizeof(szDir), sizeof(szName), sizeof(szExt)>(szBuffer, szDrive, szDir, szName, szExt);
    //_makepath_s<sizeof(szBuffer)>(szBuffer, szDrive, szDir, pszBasename, ".dll"); template NOK for gcc!
    _makepath_s(szBuffer, sizeof(szBuffer), szDrive, szDir, pszBasename, ".dll");
    m_hDll = LoadLibraryExA(szBuffer, NULL, 0x1100);
    if (m_hDll == NULL) {
#ifdef _MSC_VER
	sprintf_s<sizeof(m_szErrorMessage)>(m_szErrorMessage, "%s: failed to load library", pszBasename);
#else
	sprintf(m_szErrorMessage, "%s: failed to load library", pszBasename);
#endif
	return FALSE;
    }

    BOOL bError = FALSE;
#ifdef _MSC_VER
#define SDY_PROC(RETURN,PREFIX,NAME,SIG,ARGS) \
    if (!bError) { \
	sprintf_s<sizeof(szBuffer)>(szBuffer, "%s__%s", pszBasename, #NAME); \
	m_pfn##NAME = (Pfn##NAME) GetProcAddress(m_hDll, szBuffer); \
	if (m_pfn##NAME == NULL) { \
	    sprintf_s<sizeof(m_szErrorMessage)>(m_szErrorMessage, "%s: procedure not found", szBuffer); \
	    bError = TRUE; \
	} \
    }
#else
#define SDY_PROC(RETURN,PREFIX,NAME,SIG,ARGS) \
    if (!bError) { \
	sprintf(szBuffer, "%s__%s", pszBasename, #NAME); \
	m_pfn##NAME = (Pfn##NAME) GetProcAddress(m_hDll, szBuffer); \
	if (m_pfn##NAME == NULL) { \
	    sprintf(m_szErrorMessage, "%s: procedure not found", szBuffer); \
	    bError = TRUE; \
	} \
    }
#endif

    SDY_SIGNATURES(UNUSED)
    // panel
    if (!bError) {
	bError = LoadLayerPointers();
    }
#undef SDY_PROC

    if (bError) {
	Unload();
	return FALSE;
    }

    return TRUE;
}

BOOL CSdyDllProxy::LoadLayerPointer(PfnLayerFunction* pAddress, const  char* pszPrefix, const char* pszLayer)
{
    char szBuffer[MAX_PATH];

#ifdef _MSC_VER
    sprintf_s<sizeof(szBuffer)>(szBuffer, "%s_L_%s", pszPrefix, pszLayer);
#else
    sprintf(szBuffer, "%s_L_%s", pszPrefix, pszLayer);
#endif
    *pAddress = (PfnLayerFunction)GetProcAddress(m_hDll, szBuffer);
    if (*pAddress == NULL) {
#ifdef _MSC_VER
	sprintf_s<sizeof(m_szErrorMessage)>(m_szErrorMessage, "%s: procedure not found", szBuffer);
#else
	sprintf(m_szErrorMessage, "%s: procedure not found", szBuffer);
#endif
	return TRUE;
    }
    return FALSE;
}

BOOL CSdyDllProxy::Unload()
{
    BOOL bStatus = TRUE;

    if (m_hDll != NULL) {
	bStatus = FreeLibrary(m_hDll);
	if (bStatus) {
	    m_hDll = NULL;
	    ZeroPointers();
	}
    }
    return bStatus;
}
#endif // _WIN32
