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

#ifndef _WUX_DLL_EXT_H_513696AF_1B4F_4788_AFAE_399735605667_
#define _WUX_DLL_EXT_H_513696AF_1B4F_4788_AFAE_399735605667_

/* ---------------------------------------------------------------------------
 * extension interface and registration
 * ------------------------------------------------------------------------ */

#ifdef __cplusplus
class CWuxDllInstance
{
public:
    CWuxDllInstance();
    virtual ~CWuxDllInstance();
    // interface
    virtual BOOL OnProcessAttach(HMODULE hDllInstance);
    virtual BOOL OnThreadAttach(HMODULE hDllInstance);
    virtual BOOL OnThreadDetach(HMODULE hDllInstance);
    virtual BOOL OnProcessDetach(HMODULE hDllInstance);
};

// access to the registered instances
int WuxGetDllInstancesCount();
CWuxDllInstance** WuxGetDllInstances();
#endif /* __cplusplus */

#ifdef __cplusplus
extern "C" {
#endif

extern HMODULE WuxGetDllInstance();

#ifdef __cplusplus
}
#endif /* __cplusplus */

#endif /* _WUX_DLL_EXT_H_212A56A6_5BD3_460C_8B2E_5D68B904789C_ */
