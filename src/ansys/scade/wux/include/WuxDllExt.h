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

/**
 * @file
 * @brief Interfaces for subscribing to ``DllMain`` callbacks.
 *
 * The ``lib/WuxDllExt.cpp`` runtime file defines ``DllMain`` and calls
 * all the registered clients.
 *
 * This is relevant if and only if the target is a DLL and not a
 * standalone executable.
 */

/* ---------------------------------------------------------------------------
 * extension interface and registration
 * ------------------------------------------------------------------------ */

#ifdef __cplusplus
/**
 * @brief Base class for ``DllMain`` clients.
 *
 */
class CWuxDllInstance
{
public:
    /**
     * @brief Construct the instance and register it to ``DllMain``.
     *
     */
    CWuxDllInstance();
    /**
     * @brief Unregister the instance from ``DllMain``.
     *
     */
    virtual ~CWuxDllInstance();
    // interface
    /**
     * @brief Process the ``DLL_PROCESS_ATTACH`` notification.
     *
     * Return TRUE on success, otherwise FALSE.
     *
     * The default implementation is empty and returns True.
     * @return bool
     */
    virtual BOOL OnProcessAttach(HMODULE hDllInstance);
    /**
     * @brief Process the ``DLL_THREAD_ATTACH`` notification.
     *
     * Return TRUE on success, otherwise FALSE.
     *
     * The default implementation is empty and returns True.
     * @return bool
     */
    virtual BOOL OnThreadAttach(HMODULE hDllInstance);
    /**
     * @brief Process the ``DLL_THREAD_DETACH`` notification.
     *
     * Return TRUE on success, otherwise FALSE.
     *
     * The default implementation is empty and returns True.
     * @return bool
     */
    virtual BOOL OnThreadDetach(HMODULE hDllInstance);
    /**
     * @brief Process the ``DLL_PROCESS_DETACH`` notification.
     *
     * Return TRUE on success, otherwise FALSE.
     *
     * The default implementation is empty and returns True.
     * @return bool
     */
    virtual BOOL OnProcessDetach(HMODULE hDllInstance);
};

// access to the registered instances
/**
 * @brief Return the number of registered clients.
 * @return int
 */
int WuxGetDllInstancesCount();
/**
 * @brief Return the array of the registered clients.
 *
 * The number of elements is provided by ``WuxGetDllInstancesCount``.
 * @return CWuxDllInstance**
 */
CWuxDllInstance** WuxGetDllInstances();
#endif /* __cplusplus */

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Return the instance of the DLL.
 *
 * This handle is cached when ``DllMain`` is called with the reason
 * ``DLL_PROCESS_ATTACH``.
 * @return HMODULE
 */
extern HMODULE WuxGetDllInstance();

#ifdef __cplusplus
}
#endif /* __cplusplus */

#endif /* _WUX_DLL_EXT_H_212A56A6_5BD3_460C_8B2E_5D68B904789C_ */
