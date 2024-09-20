/*
 * Copyright (C) 2018 - 2024 ANSYS, Inc. and/or its affiliates.
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

#ifndef _A661_CONNECT_H_C0291C6F_9E27_4813_B916_35D2827EB2C6_
#define _A661_CONNECT_H_C0291C6F_9E27_4813_B916_35D2827EB2C6_

#ifdef __cplusplus
extern "C" {
#endif
extern int A661SetLogFile(const char* pszPath);
extern int A661ConnectServer(const char* pszHostName, unsigned short nPort);
extern int A661DisconnectServer();
extern size_t A661Receive(unsigned char* pszBuffer, size_t nBufSize);
extern size_t A661ReceiveEx(unsigned char* pszBuffer, size_t nBufSize, int bWait);
extern int A661Send(unsigned char* pszMessage, size_t nMsgLen);
extern int A661GetLastError(const char** ppszError);
#ifdef __cplusplus
}
#endif

#define OK                      0
#define NOTCONNECTED_ERROR      1
#define CONNECT_ERROR           2
#define RECEIVE_ERROR           3
#define SEND_ERROR              4
#define OTHER_ERROR             5
#define OVERFLOW_ERROR          6

#endif /* _A661_CONNECT_H_C0291C6F_9E27_4813_B916_35D2827EB2C6_ */
