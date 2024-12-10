#include <string.h>
#include <stdio.h>
#include "guarantee.h"
/* #include <assert.h> */

void Guarantee(int value, const char* pszContext)
{
    static int raised = 0;
    if (!value && !raised) {
	const char* p = strrchr(pszContext, '>');
	if (p) p++;
	else p = pszContext;

	printf("Guarantee error: %s\n", p);
	/* assert(value); */
	raised = 1;
    }
}
