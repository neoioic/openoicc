/* SPDX-License-Identifier: MIT */
#include <stdio.h>
#include <string.h>
#include "ho.h"
#include "neoioic.h"

extern int crt_amphicar(uint64_t *, unsigned int, unsigned int, int,
			struct object **, unsigned char *);
static unsigned int peak[5];
static int failed;

/* Exercise simultaneous distinct delegators after ordinary OBS traversal.
 * Nested VO cleanup must remove only the matching context. */
static int delegate(struct object *self, unsigned int action,
		    const struct vr *caller_context)
{
	struct vr caller = { caller_context->cr, self->oid };
	size_t index = (size_t)(self - self->nodes), i;
	unsigned int used = 0;
	for (i = 0; i < self->caller_count; i++)
		used += self->callers[i].cr != 0;
	if (used > peak[index])
		peak[index] = used;
	if (self->model_id == MSN_NEOIOIC)
		return RO_OBSOIX;
	OBS_OBJECT_INTERACT0_;
	for (i = 0; i < self->direct_base_count; i++)
		if (RN(vo_interact0(self->direct_bases[i], action, &caller)))
			failed = 1;
	return RO_OBSOIX;
}

int main(void)
{
	const unsigned int expected[] = { 1, 2, 3, 4, 2 };
	struct object *object;
	struct vr caller = { OID_MAIN, OID_MAIN };
	uint64_t oid = OID_;
	size_t i, j;
	if (RN(crt_amphicar(&oid, 0, 0, 1, &object, NULL)))
		return 1;
	for (i = 0; i < 5; i++)
		object->nodes[i].interact0 = delegate;
	if (RN(vo_interact0(object, AC0_, &caller)) || failed)
		return 2;
	for (i = 0; i < 5; i++) {
		if (peak[i] != expected[i]) {
			fprintf(stderr, "node %zu used %u seats, expected %u\n", i, peak[i], expected[i]);
			return 3;
		}
		for (j = 0; j < object->nodes[i].caller_count; j++)
			if (object->nodes[i].callers[j].cr)
				return 4;
	}
	free(object);
	puts("nested delegation seat checks passed");
	return 0;
}
