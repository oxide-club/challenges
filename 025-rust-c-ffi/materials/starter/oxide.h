/* SPDX-License-Identifier: MIT */
#ifndef OXIDE_H
#define OXIDE_H
#include <stdint.h>
#include <stddef.h>
typedef struct OcContext OcContext;
typedef struct {
    int32_t status;
    size_t written;
    size_t required;
} OcResult;
/* Complete a documentação de validade, aliasing, ownership e serialização. */
int32_t oc_create(uint8_t key, OcContext **out);
void oc_destroy(OcContext *ctx);
OcResult oc_transform(OcContext *ctx, const uint8_t *src, size_t src_len, uint8_t *dst,
                      size_t dst_cap);
uint8_t oc_rotate(uint8_t value);
#ifdef OC_TEST_HOOKS
/* Somente no build de testes; arma panic na próxima transformação elegível. */
void oc_test_panic_next(void);
#endif
#endif
