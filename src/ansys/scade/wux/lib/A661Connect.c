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

#ifdef _WIN32
#include <windows.h>
#include <stdio.h>
#include <winsock.h>

#include "A661Connect.h"

/* defaults */
#define ERRMSG_SIZE 2048
#define BUF_SIZE 256

#define DEFAULT_HOSTNAME "127.0.0.1"

/* globals */
typedef struct SA661ConnectGlobals {
    SOCKET m_SockFd;
    char m_szErrMsg[ERRMSG_SIZE];
    int m_nError;
    int m_bConnected;
    unsigned m_nPort;
    char m_szHostName[BUF_SIZE];
    const char *m_pszLogPath;
    FILE *m_fdLog;
} A661ConnectGlobals;

static A661ConnectGlobals Globals = {
    INVALID_SOCKET, "", 0, 0, 0, DEFAULT_HOSTNAME, 0, 0
};

static int A661ReconnectServer();

/*
 * Receive Message
 */
size_t A661ReceiveEx(unsigned char *pszBuffer, size_t nBufSize, int bWait)
{
    int nRecv;
    size_t len;
    unsigned long argp;
    size_t offset;

    *Globals.m_szErrMsg = '\0';

    if (A661ReconnectServer() != OK) {
        sprintf(Globals.m_szErrMsg, "not connected\n");
        Globals.m_nError = NOTCONNECTED_ERROR;
        return 0;
    }

    argp = bWait ? 0 : 1;
    ioctlsocket(Globals.m_SockFd, FIONBIO, &argp);
    /* read header */
    nRecv = recv(Globals.m_SockFd, (char *) pszBuffer, 8, 0);
    if (nRecv == SOCKET_ERROR) {
        int code = WSAGetLastError();
        switch (code) {
            case WSAEWOULDBLOCK:
                /* nothing to read */
                return OK;
            case WSAECONNRESET:
                sprintf(Globals.m_szErrMsg, "lost connection %d\n", code);
                /* disconnect */
                A661DisconnectServer();
                Globals.m_nError = NOTCONNECTED_ERROR;
                return 0;
            default:
                sprintf(Globals.m_szErrMsg, "recv error %d\n", code);
                Globals.m_nError = RECEIVE_ERROR;
                return 0;
        }
    }
    if (nRecv == 0) {
        sprintf(Globals.m_szErrMsg, "socket closed\n");
        return OK;
    }
    if (nRecv < 0) {
        sprintf(Globals.m_szErrMsg, "receive error\n");
        Globals.m_nError = RECEIVE_ERROR;
        return 0;
    }
    if (nRecv < 8) {
        sprintf(Globals.m_szErrMsg, "not enough bytes: %d (expected at least 8)\n", nRecv);
        Globals.m_nError = RECEIVE_ERROR;
        return 0;
    }
    // len = (pszBuffer[4] << 3) + (pszBuffer[5] << 2) + (pszBuffer[6] << 1) + pszBuffer[7];
    len = (pszBuffer[4] << 24) + (pszBuffer[5] << 16) + (pszBuffer[6] << 8) + pszBuffer[7];
    if (pszBuffer[0] != 0xB0) {
        sprintf(Globals.m_szErrMsg, "header error: %08x%08x\n", ((unsigned long*) pszBuffer)[0], ((unsigned long*) pszBuffer)[1]);
        Globals.m_nError = RECEIVE_ERROR;
        return 0;
    }
    if (len > nBufSize) {
        sprintf(Globals.m_szErrMsg, "buffer overflow %zu (max %zu)\n", len, nBufSize);
        Globals.m_nError = OVERFLOW_ERROR;
        return 0;
    }

    /* read message */
    for (offset = nRecv; offset < len; offset += nRecv) {
        nRecv = recv(Globals.m_SockFd, (char *) &pszBuffer[offset], (int) (len - offset), 0);
        if (nRecv < 0) {
            sprintf(Globals.m_szErrMsg, "receive error\n");
            Globals.m_nError = RECEIVE_ERROR;
            return 0;
        }
    }

    if (Globals.m_fdLog != NULL) {
        size_t i, j, k;
        fprintf(Globals.m_fdLog, "receive buffer:\n");
        for (i = 0; i < len; i += 16) {
            for (j = i; j < (i + 16) && j < len; j += 4) {
                for (k = j; k < (j + 4) && k < len; k++) {
                    fprintf(Globals.m_fdLog, "%.2x ", pszBuffer[k]);
                }
                fprintf(Globals.m_fdLog, "  ");
            }
            fprintf(Globals.m_fdLog, "\n");
        }
        fprintf(Globals.m_fdLog, "\n");
        fflush(Globals.m_fdLog);
    }

    // return OK;
    return (int) len;
}

size_t A661Receive(unsigned char* pszBuffer, size_t nBufSize)
{
    // former implementation does not wait
    return A661ReceiveEx(pszBuffer, nBufSize, 0);
}

/*
 * Send Message
 */
int A661Send(unsigned char *msg, size_t msg_len)
{
    unsigned long argp = 0;

    if (Globals.m_fdLog != NULL) {
        size_t i, j, k;
        fprintf(Globals.m_fdLog, "send buffer:\n");
        for (i = 0; i < msg_len; i += 16) {
            for (j = i; j < (i + 16) && j < msg_len; j += 4) {
                for (k = j; k < (j + 4) && k < msg_len; k++) {
                    fprintf(Globals.m_fdLog, "%.2x ", msg[k]);
                }
                fprintf(Globals.m_fdLog, "  ");
            }
            fprintf(Globals.m_fdLog, "\n");
        }
        fprintf(Globals.m_fdLog, "\n");
        fflush(Globals.m_fdLog);
    }

    if (!Globals.m_bConnected) {
        return NOTCONNECTED_ERROR;
    }

    ioctlsocket(Globals.m_SockFd, FIONBIO, &argp);
    if (send(Globals.m_SockFd, (char *) msg, (int) msg_len, 0) != msg_len) {
        return SEND_ERROR;
    }

    return OK;
}

/*
 *
 */
static int IsLocalHost(char *pszHostName)
{
    int bIsLocalHost;

    WSADATA WSAData;
    char szHostName[128] = "";
    struct sockaddr_in SocketAddress;
    struct hostent *pHost = 0;
    int iCnt;

    bIsLocalHost = 0;

    if (!strcmp(pszHostName, "127.0.0.1"))
        return 1;


    /* Initialize winsock dll */
    if (WSAStartup(MAKEWORD(1, 0), &WSAData)) {
        /* REGISTER_ERROR(OTHER_ERROR, "WSAStartup error"); */
        return bIsLocalHost;
    }


    /* Get local host name */
    if (gethostname(szHostName, sizeof(szHostName))) {
        /* Error handling -> call 'WSAGetLastError()' */
        /* REGISTER_ERROR(OTHER_ERROR, "gethostname error"); */
        return bIsLocalHost;
    }

    /* Get local IP addresses */
    pHost = gethostbyname(szHostName);
    if (!pHost) {
        /* Error handling -> call 'WSAGetLastError()' */
        /* REGISTER_ERROR(OTHER_ERROR, "gethostbyname error"); */
        return bIsLocalHost;
    }

    for (iCnt = 0; pHost->h_addr_list[iCnt]; ++iCnt) {
        char szIp[128];
        memcpy(&SocketAddress.sin_addr, pHost->h_addr_list[iCnt], pHost->h_length);
        strcpy_s(szIp, sizeof(szIp), inet_ntoa(SocketAddress.sin_addr));
        if (!strcmp(szIp, pszHostName)) {
            bIsLocalHost = 1;
        }
    }

    /* Cleanup */
    WSACleanup();
    return bIsLocalHost;
}

/*
 *Connect Server
 */
static int A661ReconnectServer()
{
    struct sockaddr_in servaddr;
    SOCKET nSockFd;

    if (Globals.m_bConnected) {
        return OK;
    }

    /* close previous connection */
    /*if (Globals.m_SockFd != 0)
       close(Globals.m_SockFd); */

    /* try to connect to server */
    if ((nSockFd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        return OTHER_ERROR;
    }

    memset((struct sockaddr*)&servaddr, 0, sizeof(struct sockaddr_in));
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(Globals.m_nPort);
    servaddr.sin_addr.s_addr = inet_addr(Globals.m_szHostName);

    if (connect(nSockFd, (struct sockaddr*)&servaddr, sizeof(servaddr)) != 0) {
        return CONNECT_ERROR;
    }

    printf("connected to A661 server\n");

    Globals.m_bConnected = 1;
    Globals.m_SockFd = nSockFd;
    return OK;
}

/*
 *Connect Server
 */
int A661ConnectServer(const char* pszHostName, unsigned short nPort)
{
    WSADATA wsaData;

    if (Globals.m_bConnected) {
	return OK;
    }

    if (Globals.m_pszLogPath) {
        fopen_s(&Globals.m_fdLog, Globals.m_pszLogPath, "w");
    }

    /* create socket */
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        return OTHER_ERROR;
    }

    Globals.m_nPort = nPort;
    strcpy_s(Globals.m_szHostName, sizeof(Globals.m_szHostName), pszHostName);

    return A661ReconnectServer(pszHostName, nPort);
}

/*
*Disconnect Server
*/
int A661DisconnectServer()
{
    if (Globals.m_bConnected) {
	closesocket(Globals.m_SockFd);
	Globals.m_SockFd = 0;
	Globals.m_bConnected = 0;
        printf("disconnected from A661 server\n");
    }
    WSACleanup();
    return OK;
}

int A661SetLogFile(const char *pszPath)
{
    Globals.m_pszLogPath = pszPath;
    return OK;
}

int A661GetLastError(const char** ppszError)
{
    *ppszError = Globals.m_szErrMsg;
    return Globals.m_nError;
}
#endif /* _WIN32 */
