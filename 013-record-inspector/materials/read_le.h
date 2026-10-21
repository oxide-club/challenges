/* Disponível após validar que há dois bytes no buffer. */
#include <stdint.h>
static inline uint16_t read_le16(const unsigned char *p) { return (uint16_t)((unsigned)p[0] | ((unsigned)p[1] << 8)); }
