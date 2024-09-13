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

#ifndef _SDY_EXT_H_158ED1CF_4974_48A1_94C5_8EFC6007E589_
#define _SDY_EXT_H_158ED1CF_4974_48A1_94C5_8EFC6007E589_
 // {158ED1CF_4974_48A1_94C5_8EFC6007E589}

#ifdef __cplusplus
extern "C" {
#endif

 /* ---------------------------------------------------------------------------
  * DLL management
  * ------------------------------------------------------------------------ */

int WuxLoadSdyDlls(/*HINSTANCE*/ void* hinstDll);
int WuxUnloadSdyDlls(/*HINSTANCE*/ void* hinstDll);

/* ---------------------------------------------------------------------------
 * SCADE Display Extension interface
 * ------------------------------------------------------------------------ */

void WuxSdyInit();
void WuxSdyDraw();
void WuxSdySetInputs();
void WuxSdyGetOutputs();
int WuxSdyCancelled();

#ifdef WUX_DISPLAY_AS_BUFFERS
typedef struct _WuxSdyScreen
{
    const char* name;
    int width;
    int height;
    const char* buffer; /* RGBA */
    int size;
} WuxSdyScreen;

int WuxSdyGetScreenCount();
const WuxSdyScreen* WuxSdyGetScreen(int index);
#endif

#ifdef __cplusplus
}
#endif

#endif /* _SDY_EXT_H_158ED1CF_4974_48A1_94C5_8EFC6007E589_ */
