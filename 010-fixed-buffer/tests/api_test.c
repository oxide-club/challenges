#include "api.h"
#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
int main(void) {
  unsigned char region[6] = {11, 0, 0, 0, 0, 22};
  Buffer b;
  buffer_init(&b, region + 1, 4);
  unsigned char x[] = {0, 1, 0, 255};
  assert(buffer_append(&b, x, 4));
  assert(!buffer_append(&b, NULL, SIZE_MAX));
  assert(!buffer_append(&b, x, 1));
  assert(b.size == 4 && !memcmp(b.data, x, 4));
  assert(region[0] == 11 && region[5] == 22);
  buffer_clear(&b);
  assert(b.size == 0 && b.capacity == 4);
  assert(buffer_append(&b, NULL, 0));
  return 0;
}
