#include "api.h"
#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
int main(void) {
  _Alignas(16) unsigned char region[256];
  Pool p;
  pool_init(&p, region, 256);
  void *ptr[32];
  for (size_t i = 0; i < 32; i++) {
    ptr[i] = pool_alloc(&p, 1);
    assert(ptr[i] == region + i * 8);
    memset(ptr[i], (int)i, 8);
  }
  assert(!pool_alloc(&p, 1));
  for (size_t i = 0; i < 32; i++)
    for (size_t j = 0; j < 8; j++)
      assert(((unsigned char *)ptr[i])[j] == i);
  for (size_t i = 0; i < 32; i += 2)
    pool_free(&p, ptr[i]);
  assert(!pool_alloc(&p, 16));
  for (size_t i = 1; i < 32; i += 2)
    pool_free(&p, ptr[i]);
  assert(p.count == 1 && p.blocks[0].offset == 0 && p.blocks[0].size == 256 &&
         !p.blocks[0].used);
  assert(!pool_alloc(&p, SIZE_MAX) && p.count == 1);
  assert(pool_alloc(&p, 256) == region);
  assert(!pool_alloc(&p, 1));
  /* Uma divisão exige um descritor; encaixe exato não exige outro. */
  _Alignas(16) unsigned char large_region[8200];
  pool_init(&p, large_region, sizeof large_region);
  for (size_t i = 0; i < 1023; i++)
    assert(pool_alloc(&p, 8) == large_region + i * 8);
  assert(p.count == BLOCK_LIMIT);
  assert(p.blocks[1023].offset == 8184 && p.blocks[1023].size == 16 &&
         !p.blocks[1023].used);
  Block snapshot[BLOCK_LIMIT];
  memcpy(snapshot, p.blocks, sizeof snapshot);
  assert(!pool_alloc(&p, 8));
  assert(p.count == BLOCK_LIMIT && p.capacity == sizeof large_region);
  assert(!memcmp(snapshot, p.blocks, sizeof snapshot));
  assert(pool_alloc(&p, 16) == large_region + 8184);
  assert(p.count == BLOCK_LIMIT && p.blocks[1023].size == 16 &&
         p.blocks[1023].used);
  return 0;
}
