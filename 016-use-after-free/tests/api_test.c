#include "api.h"
#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
int main(void) {
  unsigned char src[] = {0, 255, 42};
  unsigned char *p = copy_bytes(src, 3);
  assert(p && p != src && !memcmp(p, src, 3));
  src[2] = 7;
  assert(p[2] == 42);
  free(p);
  p = copy_bytes(NULL, 0);
  assert(p);
  free(p);
  return 0;
}
