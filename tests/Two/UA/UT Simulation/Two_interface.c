#include "Two_interface.h"
#include "Two_type.h"
#include "Two_mapping.h"
#include "SmuVTable.h"
#include <string.h>

#define UNUSED(x) (void)(x)
/* context */

inC_Two inputs_ctx;
static inC_Two inputs_ctx_execute;
outC_Two outputs_ctx;

static void _SCSIM_RestoreInterface(void) {
    init_msg_float_a661_types(&inputs_ctx.duThrottleChangedLeft);
    init_msg_float_a661_types(&inputs_ctx_execute.duThrottleChangedLeft);
    init_msg_float_a661_types(&inputs_ctx.duThrottleChangedRight);
    init_msg_float_a661_types(&inputs_ctx_execute.duThrottleChangedRight);
    init_msg_uint8_a661_types(&inputs_ctx.duThrottleLockState);
    init_msg_uint8_a661_types(&inputs_ctx_execute.duThrottleLockState);
    init_Power(&inputs_ctx.acPower);
    init_Power(&inputs_ctx_execute.acPower);
    memset((void*)&outputs_ctx, 0, sizeof(outputs_ctx));
}

static void _SCSIM_ExecuteInterface(void) {
    pSimulator->m_pfnAcquireValueMutex(pSimulator);
    kcg_copy_msg_float_a661_types(&inputs_ctx_execute.duThrottleChangedLeft, &inputs_ctx.duThrottleChangedLeft);
    kcg_copy_msg_float_a661_types(&inputs_ctx_execute.duThrottleChangedRight, &inputs_ctx.duThrottleChangedRight);
    kcg_copy_msg_uint8_a661_types(&inputs_ctx_execute.duThrottleLockState, &inputs_ctx.duThrottleLockState);
    kcg_copy_Power(&inputs_ctx_execute.acPower, &inputs_ctx.acPower);
    pSimulator->m_pfnReleaseValueMutex(pSimulator);
}

#ifdef __cplusplus
extern "C" {
#endif

const int  rt_version = Srtv62;

const char* _SCSIM_CheckSum = "afa80709aa514801d807e31169021f46";
const char* _SCSIM_SmuTypesCheckSum = "e199405d867d4446e9a5ba6df64b408e";

/* simulation */

int SimInit(void) {
    int nRet = 0;
    _SCSIM_RestoreInterface();
#ifdef EXTENDED_SIM
    BeforeSimInit();
#endif
#ifndef KCG_USER_DEFINED_INIT
    Two_init(&outputs_ctx);
    nRet = 1;
#else
    nRet = 0;
#endif
#ifdef EXTENDED_SIM
    AfterSimInit();
#endif
    return nRet;
}

int SimReset(void) {
    int nRet = 0;
    _SCSIM_RestoreInterface();
#ifdef EXTENDED_SIM
    BeforeSimInit();
#endif
#ifndef KCG_NO_EXTERN_CALL_TO_RESET
    Two_reset(&outputs_ctx);
    nRet = 1;
#else
    nRet = 0;
#endif
#ifdef EXTENDED_SIM
    AfterSimInit();
#endif
    return nRet;
}

#ifdef __cplusplus
    #ifdef pSimoutC_TwoCIVTable_defined
        extern struct SimCustomInitVTable *pSimoutC_TwoCIVTable;
    #else
        struct SimCustomInitVTable *pSimoutC_TwoCIVTable = NULL;
    #endif
#else
    struct SimCustomInitVTable *pSimoutC_TwoCIVTable;
#endif

int SimCustomInit(void) {
    int nRet = 0;
    if (pSimoutC_TwoCIVTable != NULL &&
        pSimoutC_TwoCIVTable->m_pfnCustomInit != NULL) {
        /* VTable function provided => call it */
        nRet = pSimoutC_TwoCIVTable->m_pfnCustomInit ((void*)&outputs_ctx);
    }
    else {
        /* VTable missing => error */
        nRet = 0;
    }
    return nRet;
}

#ifdef EXTENDED_SIM
    int GraphicalInputsConnected = 1;
#endif

int SimStep(void) {
#ifdef EXTENDED_SIM
    if (GraphicalInputsConnected)
        BeforeSimStep();
#endif
    _SCSIM_ExecuteInterface();
    Two(&inputs_ctx_execute, &outputs_ctx);
#ifdef EXTENDED_SIM
    AfterSimStep();
#endif
    return 1;
}

int SimStop(void) {
#ifdef EXTENDED_SIM
    ExtendedSimStop();
#endif
    return 1;
}

void SsmUpdateValues(void) {
#ifdef EXTENDED_SIM
    UpdateValues();
#endif
}

void SsmConnectExternalInputs(int bConnect) {
#ifdef EXTENDED_SIM
    GraphicalInputsConnected = bConnect;
#else
    UNUSED(bConnect);
#endif
}

/* dump */

int SsmGetDumpSize(void) {
    int nSize = 0;
    nSize += sizeof(inC_Two);
    nSize += sizeof(outC_Two);
#ifdef EXTENDED_SIM
    nSize += ExtendedGetDumpSize();
#endif
    return nSize;
}

void SsmGatherDumpData(char * pData) {
    char* pCurrent = pData;
    memcpy(pCurrent, &inputs_ctx, sizeof(inC_Two));
    pCurrent += sizeof(inC_Two);
    memcpy(pCurrent, &outputs_ctx, sizeof(outC_Two));
    pCurrent += sizeof(outC_Two);
#ifdef EXTENDED_SIM
    ExtendedGatherDumpData(pCurrent);
#endif
}

void SsmRestoreDumpData(const char * pData) {
    const char* pCurrent = pData;
    memcpy(&inputs_ctx, pCurrent, sizeof(inC_Two));
    pCurrent += sizeof(inC_Two);
    memcpy(&outputs_ctx, pCurrent, sizeof(outC_Two));
    pCurrent += sizeof(outC_Two);
#ifdef EXTENDED_SIM
    ExtendedRestoreDumpData(pCurrent);
#endif
}

/* snapshot */

int SsmSaveSnapshot(const char * szFilePath, size_t nCycle) {
    /* Test Services API not available */
    UNUSED(szFilePath);
    UNUSED(nCycle);
    return 0;
}

int SsmLoadSnapshot(const char * szFilePath, size_t *nCycle) {
    /* Test Services API not available */
    UNUSED(szFilePath);
    UNUSED(nCycle);
    return 0;
}

/* checksum */

const char * SsmGetCheckSum() {
    return _SCSIM_CheckSum;
}

const char * SsmGetSmuTypesCheckSum() {
    return _SCSIM_SmuTypesCheckSum;
}

#ifdef __cplusplus
} /* "C" */
#endif

