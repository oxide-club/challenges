/* SPDX-License-Identifier: MIT. Liberação de contextos sem injeção de panic. */
#include "oxide.h"
#include <assert.h>
#include <stdint.h>
#include <stddef.h>
int main(void) {
    for (unsigned i = 0; i < 32; i++) {
        OcContext *ctx = NULL;
        assert(oc_create((uint8_t)i, &ctx) == 0 && ctx);
        uint8_t source = 1, destination = 0;
        OcResult r = oc_transform(ctx, &source, 1, &destination, 1);
        assert(r.status == 0 && r.written == 1 && r.required == 1);
        oc_destroy(ctx);
    }
    oc_destroy(NULL);
}
