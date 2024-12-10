#ifndef _GUARANTEE_H_
#define _GUARANTEE_H_

extern void Guarantee(int value, const char* pszContext);

#ifndef EXTENDED_SIM

#define kcg_guarantee(V) Guarantee(V, #V)

#endif

#endif /* _GUARANTEE_H_ */
