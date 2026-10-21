#include "api.h"
#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
int main(void) {
  _Alignas(16) unsigned char region[128];
  Arena a;
  arena_init(&a, region, sizeof region);
  for (size_t align = 1; align <= 16; align *= 2) {
    size_t before = a.used;
    unsigned char *p = arena_alloc(&a, 3, align);
    assert(p && ((uintptr_t)p % align) == 0 && (size_t)(p - region) >= before);
    memset(p, 42, 3);
  }
  size_t used = a.used;
  assert(!arena_alloc(&a, SIZE_MAX, 16) && a.used == used);
  assert(!arena_alloc(&a, 1, 3) && a.used == used);
  assert(!arena_alloc(&a, 0, 1) && a.used == used);
  arena_reset(&a);
  assert(!a.used);
  assert(arena_alloc(&a, 128, 16) == region);
  assert(!arena_alloc(&a, 1, 1) && a.used == 128);
  return 0;
}
