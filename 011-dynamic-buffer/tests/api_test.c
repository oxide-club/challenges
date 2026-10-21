#include "api.h"
#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
static int fail_next;
static size_t calls;
static void *resize(void *p, size_t n) {
  calls++;
  if (fail_next) {
    fail_next = 0;
    return NULL;
  }
  return realloc(p, n);
}
int main(void) {
  Buffer b;
  buffer_init(&b, resize);
  unsigned char x[] = {0, 1, 255};
  for (int i = 0; i < 100; i++)
    assert(buffer_append(&b, x, 3));
  assert(b.size == 300 && b.capacity == 512);
  for (int i = 0; i < 100; i++)
    assert(!memcmp(b.data + i * 3, x, 3));
  unsigned char *old = b.data;
  size_t cap = b.capacity;
  size_t calls_before = calls;
  assert(!buffer_append(&b, NULL, SIZE_MAX));
  assert(calls == calls_before && b.data == old && b.size == 300 &&
         b.capacity == cap);
  fail_next = 1;
  unsigned char more[300] = {0};
  assert(!buffer_append(&b, more, 300));
  assert(b.data == old && b.size == 300 && b.capacity == cap);
  assert(buffer_append(&b, more, 300));
  assert(b.size == 600 && b.capacity == 1024);
  buffer_destroy(&b);
  assert(!b.data && !b.size && !b.capacity);
  buffer_destroy(&b);
  return 0;
}
