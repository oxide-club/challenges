/* SPDX-License-Identifier: MIT. Compara bytes explícitos sem usar as rotinas testadas como oráculo. */
#include <stddef.h>
extern void *memcpy(void *, const void *, size_t);
extern void *memmove(void *, const void *, size_t);
extern void *memset(void *, int, size_t);
extern int memcmp(const void *, const void *, size_t);
extern int bcmp(const void *, const void *, size_t);
extern size_t strlen(const char *);
#define CHECK(x)                                                                                   \
    do {                                                                                           \
        if (!(x))                                                                                  \
            return __LINE__;                                                                       \
    } while (0)
int main(void) {
    unsigned char a[8] = {0, 1, 2, 3, 4, 5, 6, 7};
    unsigned char b[8] = {0};
    CHECK(memcpy(b, a, 8) == b);
    for (int i = 0; i < 8; i++)
        CHECK(b[i] == i);
    CHECK(memmove(a + 1, a, 7) == a + 1);
    for (int i = 1; i < 8; i++)
        CHECK(a[i] == i - 1);
    CHECK(memmove(a, a + 1, 7) == a);
    for (int i = 0; i < 7; i++)
        CHECK(a[i] == i);
    CHECK(memset(b, 0xa5, 8) == b);
    for (int i = 0; i < 8; i++)
        CHECK(b[i] == 0xa5);
    CHECK(memcmp(a, b, 8) < 0);
    CHECK(memcmp(b, a, 8) > 0);
    CHECK(bcmp(a, a, 8) == 0);
    CHECK(bcmp(a, b, 8) != 0);
    CHECK(bcmp(b, a, 8) != 0);
    CHECK(memcpy(0, 0, 0) == 0);
    CHECK(memmove(0, 0, 0) == 0);
    CHECK(memset(0, 0, 0) == 0);
    CHECK(memcmp(0, 0, 0) == 0);
    CHECK(bcmp(0, 0, 0) == 0);
    CHECK(strlen("") == 0);
    CHECK(strlen("abc") == 3);
    return 0;
}
