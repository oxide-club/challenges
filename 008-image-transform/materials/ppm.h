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
static int ppm_dimension(FILE *f, int delim, size_t *v) {
  int c = fgetc(f);
  size_t n = 0;
  int digits = 0;
  while (c >= '0' && c <= '9') {
    if (++digits > 3)
      return 0;
    n = n * 10 + (unsigned)(c - '0');
    c = fgetc(f);
  }
  if (c != delim || n < 1 || n > 256)
    return 0;
  *v = n;
  return 1;
}
static int ppm_read(FILE *f, Image *im) {
  im->pixels = NULL;
  if (fgetc(f) != 'P' || fgetc(f) != '6' || fgetc(f) != '\n')
    return 0;
  if (!ppm_dimension(f, ' ', &im->w) || !ppm_dimension(f, '\n', &im->h))
    return 0;
  if (fgetc(f) != '2' || fgetc(f) != '5' || fgetc(f) != '5' || fgetc(f) != '\n')
    return 0;
  size_t n = im->w * im->h * 3;
  im->pixels = malloc(n);
  if (!im->pixels)
    return 0;
  if (fread(im->pixels, 1, n, f) != n || fgetc(f) != EOF || ferror(f)) {
    free(im->pixels);
    im->pixels = NULL;
    return 0;
  }
  return 1;
}
static int ppm_write(FILE *f, const Image *im) {
  return fprintf(f, "P6\n%zu %zu\n255\n", im->w, im->h) > 0 &&
         fwrite(im->pixels, 3, im->w * im->h, f) == im->w * im->h;
}
#endif
