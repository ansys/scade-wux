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

#ifndef _WUX_SDY_DLL_H_16CFE415_3010_4598_8190_2BC78EA7EAFF_
#define _WUX_SDY_DLL_H_16CFE415_3010_4598_8190_2BC78EA7EAFF_

 /* ---------------------------------------------------------------------------
 * SCADE Display DLL exported functions
 * ------------------------------------------------------------------------ */

// exported function wrapping
#define SDY_SIGNATURES(PREFIX) \
    SDY_PROC(int, PREFIX, lockio, (), ()) \
    SDY_PROC(int, PREFIX, unlockio, (), ()) \
    SDY_PROC(int, PREFIX, init, (), ()) \
    SDY_PROC(int, PREFIX, draw, (), ())\
    SDY_PROC(int, PREFIX, cancelled, (), ()) \
    SDY_PROC(int, PREFIX, refreshCallback, (T_COSIM_REFRESH_CALLBACK f), (f)) \
    SDY_PROC(/*RGBA*/char*, PREFIX, init_buffer, (), ()) \
    SDY_PROC(int, PREFIX, screen_width, (), ()) \
    SDY_PROC(int, PREFIX, screen_height, (), ()) \
    SDY_PROC(int, PREFIX, nb_pointers, (), ()) \
    SDY_PROC(int, PREFIX, nb_keyboards, (), ()) \
    SDY_PROC(sdy_pointer_event_t*, PREFIX, pointer_event, (int index), (index)) \
    SDY_PROC(sdy_keyboard_event_t*, PREFIX, keyboard_event, (int index), (index))

//{{ typedefs
#define SDY_PROC(RETURN,PREFIX,NAME,SIG,ARGS) \
    typedef RETURN (*Pfn##NAME)SIG;

// unused prefix
SDY_SIGNATURES(UNUSED)
#undef SDY_PROC
//}}

typedef void* (*PfnLayerFunction)();

// proxy class
class CSdyDllProxy
{
public:
    CSdyDllProxy();
    ~CSdyDllProxy();

    BOOL Load(HINSTANCE hinstDll, const char* pszBasename);
    BOOL Unload();

    const char* GetLastError() const;

    //{{ proxies
#define SDY_PROC(RETURN,PREFIX,NAME,SIG,ARGS) \
    RETURN NAME SIG;

    SDY_SIGNATURES(UNUSED)
#undef SDY_PROC
    //}}

protected:
    HMODULE m_hDll;
    char m_szErrorMessage[4096];

    //{{ function pointers declaration
#define SDY_PROC(RETURN,PREFIX,NAME,SIG,ARGS) \
    Pfn##NAME m_pfn##NAME;

    SDY_SIGNATURES(UNUSED)
#undef SDY_PROC
    //}}

    // raz
    virtual void ZeroPointers();
    // additional functions
    virtual BOOL LoadLayerPointers() = 0;
    BOOL LoadLayerPointer(PfnLayerFunction* pAddress, const  char* pszPrefix, const char* pszLayer);
};

//{{ inlines
#define SDY_PROC(RETURN,PREFIX,NAME,SIG,ARGS) \
    inline RETURN CSdyDllProxy::NAME SIG \
    { \
	return m_pfn##NAME == NULL ? 0 : m_pfn##NAME ARGS; \
    }

SDY_SIGNATURES(UNUSED)
#undef SDY_PROC
//}}

// helpers for defining DLL proxy instances
#define DEF_SDY_DLL_PROC(RETURN,PREFIX,NAME,SIG,ARGS) \
    RETURN PREFIX##__##NAME SIG \
    { \
	return h##PREFIX.NAME ARGS; \
    }

#define DEF_SDY_DLL_INSTANCE(PREFIX) \
    C##PREFIX##DllProxy h##PREFIX; \
    SDY_SIGNATURES(PREFIX)

#endif /* _WUX_SDY_DLL_H_16CFE415_3010_4598_8190_2BC78EA7EAFF_ */
