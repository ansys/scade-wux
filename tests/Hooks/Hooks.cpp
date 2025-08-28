#include "WuxSimuExt.h"
extern "C" {
#include "wuxctxHooks.h"
}

static class Hooks : public CWuxSimulatorExtension
{
public:
    void BeforeSimStep()
    {
        // initialize the sensor from the probe
	// do not use regular s_P variable but simulator's _ctx_s_P_buffer
	_ctx_s_P_buffer = outputs_ctx.nextSensor;
    }
} hooks;
