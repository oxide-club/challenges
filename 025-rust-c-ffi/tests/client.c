/* SPDX-License-Identifier: MIT. Casos derivados do contrato, sem ponteiros forjados. */
#include "oxide.h"
#include "expected.h"
#include <assert.h>
#include <limits.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
static unsigned rotate_calls;
extern uint8_t __real_oc_rotate(uint8_t value);
uint8_t __wrap_oc_rotate(uint8_t value) {
    rotate_calls++;
    return __real_oc_rotate(value);
}
static void check_result(int line, OcResult r, int status, size_t written, size_t required) {
    if (r.status != status || r.written != written || r.required != required)
        fprintf(stderr, "client.c:%d: obtido=(%d,%zu,%zu), esperado=(%d,%zu,%zu)\n", line, r.status,
                r.written, r.required, status, written, required);
    assert(r.status == status);
    assert(r.written == written);
    assert(r.required == required);
}
#define result(r, s, w, n) check_result(__LINE__, r, s, w, n)
int main(void) {
    assert(sizeof(OcResult) == 24 && _Alignof(OcResult) == 8);
    assert(offsetof(OcResult, status) == 0 && offsetof(OcResult, written) == 8 &&
           offsetof(OcResult, required) == 16);
    assert(oc_create(0, NULL) == 1);
    OcContext *ctx = NULL;
    assert(oc_create(0, &ctx) == 0 && ctx);
    const uint8_t src[] = {0, 1, 128, 255};
    uint8_t dst[6];
    memset(dst, 0xa5, sizeof dst);
    result(oc_transform(ctx, src, 4, dst, 3), 2, 0, 4);
    for (unsigned i = 0; i < 6; i++)
        assert(dst[i] == 0xa5);
    result(oc_transform(ctx, src, 4, NULL, 0), 2, 0, 4);
    rotate_calls = 0;
    result(oc_transform(ctx, src, 4, dst, 6), 0, 4, 4);
    assert(rotate_calls == 4);
    const uint8_t want[] = {0, 2, 1, 255, 0xa5, 0xa5};
    assert(memcmp(dst, want, 6) == 0);
    result(oc_transform(ctx, NULL, 0, NULL, 0), 0, 0, 0);
    result(oc_transform(NULL, NULL, 0, NULL, 0), 1, 0, 0);
    result(oc_transform(ctx, NULL, 1, dst, 6), 1, 0, 0);
    result(oc_transform(ctx, src, 4, NULL, 1), 1, 0, 0);
    result(oc_transform(ctx, src, (size_t)PTRDIFF_MAX + 1, dst, 6), 1, 0, 0);
    result(oc_transform(ctx, src, 4, dst, (size_t)PTRDIFF_MAX + 1), 1, 0, 0);
    result(oc_transform(ctx, src, SIZE_MAX, dst, 6), 1, 0, 0);
    result(oc_transform(ctx, src, 4, dst, SIZE_MAX), 1, 0, 0);
    oc_test_panic_next();
    result(oc_transform(ctx, NULL, 1, dst, 6), 1, 0, 0);
    result(oc_transform(ctx, src, 4, dst, 3), 2, 0, 4);
    result(oc_transform(ctx, src, 4, dst, 6), 3, 0, 0);
    memset(dst, 0xa5, 6);
    result(oc_transform(ctx, src, 4, dst, 6), 4, 0, 0);
    result(oc_transform(ctx, src, 4, dst, 0), 4, 0, 0);
    result(oc_transform(ctx, src, (size_t)PTRDIFF_MAX + 1, dst, 6), 1, 0, 0);
    result(oc_transform(ctx, src, 4, dst, (size_t)PTRDIFF_MAX + 1), 1, 0, 0);
    result(oc_transform(ctx, src, SIZE_MAX, dst, 6), 1, 0, 0);
    result(oc_transform(ctx, src, 4, dst, SIZE_MAX), 1, 0, 0);
    result(oc_transform(ctx, NULL, 1, dst, 6), 1, 0, 0);
    for (unsigned i = 0; i < 6; i++)
        assert(dst[i] == 0xa5);
    oc_destroy(ctx);
    oc_destroy(NULL);
    ctx = NULL;
    assert(oc_create(0x5a, &ctx) == 0);
    const uint8_t mixed[] = {0, 0x5a, 0xff, 0x80};
    const uint8_t expected[] = {0xb4, 0, 0x4b, 0xb5};
    result(oc_transform(ctx, mixed, 4, dst, 6), 0, 4, 4);
    assert(memcmp(dst, expected, 4) == 0);
    oc_destroy(ctx);
    for (unsigned k = 0; k < 2; k++) {
        assert(oc_create(k ? 90 : 0, &ctx) == 0);
        for (unsigned v = 0; v < 256; v++) {
            uint8_t value = (uint8_t)v, output = 0xa5;
            result(oc_transform(ctx, &value, 1, &output, 1), 0, 1, 1);
            assert(output == expected_bytes[k][v]);
        }
        oc_destroy(ctx);
    }
    puts("API C: layout, bytes, precedência, panic e poison conferidos");
}
