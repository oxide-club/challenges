/* SPDX-License-Identifier: MIT. Destruição de contextos envenenados válidos. */
#include "oxide.h"
#include <assert.h>
#include <stddef.h>
int main(void) {
    for (unsigned i = 0; i < 8; i++) {
        OcContext *ctx = NULL;
        assert(oc_create(0, &ctx) == 0 && ctx);
        const uint8_t source = 1;
        uint8_t destination = 0;
        oc_test_panic_next();
        OcResult r = oc_transform(ctx, &source, 1, &destination, 1);
        assert(r.status == 3 && r.written == 0 && r.required == 0);
        r = oc_transform(ctx, &source, 1, &destination, 1);
        assert(r.status == 4 && r.written == 0 && r.required == 0);
        oc_destroy(ctx);
    }
}
