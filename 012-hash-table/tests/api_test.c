#include "api.h"
#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
static int fail_next;
static void *allocate(size_t n) {
  if (fail_next) {
    fail_next = 0;
    return NULL;
  }
  return malloc(n);
}
int main(void) {
  Table t;
  table_init(&t, allocate);
  for (int32_t i = 0; i < 200; i++)
    assert(table_put(&t, i * 256, i - 100));
  assert(t.count == 200);
  for (int32_t i = 0; i < 200; i++) {
    int32_t v = 777;
    assert(table_get(&t, i * 256, &v) && v == i - 100);
    assert(table_put(&t, i * 256, 100 - i));
  }
  assert(t.count == 200);
  for (int32_t i = 0; i < 200; i++) {
    int32_t v;
    assert(table_get(&t, i * 256, &v) && v == 100 - i);
  }
  int32_t untouched = 99;
  assert(!table_get(&t, 1, &untouched) && untouched == 99);
  table_destroy(&t);
  table_init(&t, allocate);
  for (int32_t i = 0; i < 4; i++)
    assert(table_put(&t, i * 8, i));
  Pair *old = t.pairs;
  fail_next = 1;
  assert(!table_put(&t, 32, 99));
  assert(t.pairs == old && t.count == 4 && t.capacity == 8);
  for (int32_t i = 0; i < 4; i++) {
    int32_t v;
    assert(table_get(&t, i * 8, &v) && v == i);
  }
  assert(table_put(&t, 32, 99));
  table_destroy(&t);
  return 0;
}
