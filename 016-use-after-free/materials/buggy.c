#include <stdio.h>
#include <stdlib.h>
#include <string.h>
/* O produtor pensa que já terminou, mas o consumidor ainda precisa da cópia. */
static unsigned char *produce(void) {
  unsigned char *p = malloc(4);
  if (!p)
    exit(2);
  memcpy(p, "Oxid", 4);
  free(p);
  return p;
}
int main(void) {
  unsigned char *p = produce();
  printf("%02x\n", p[0]);
  return 0;
}
