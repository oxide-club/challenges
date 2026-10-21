/* Subconjunto P6 estrito: P6\nW H\n255\n, W,H decimais 1..256.
   Sem comentários, espaços adicionais ou imagens concatenadas. */
#ifndef OXIDE_PPM_H
#define OXIDE_PPM_H
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
typedef struct {
  size_t w, h;
  unsigned char *pixels;
} Image;
static int ppm_write(FILE *f, const Image *im) {
  return fprintf(f, "P6\n%zu %zu\n255\n", im->w, im->h) > 0 &&
         fwrite(im->pixels, 3, im->w * im->h, f) == im->w * im->h;
}
#endif
