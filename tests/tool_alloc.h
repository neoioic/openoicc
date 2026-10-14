/* SPDX-License-Identifier: MIT */
#include "alloc.h"
void *test_realloc(void *memory, size_t size);
#define realloc test_realloc
