/* SPDX-License-Identifier: MIT */
#include <stdio.h>
#include <string.h>
#include <limits.h>
#include "ho.h"
#include "openoicc/construct.h"
#include "alloc.h"

extern int crt_amphicar(uint64_t *, unsigned int, unsigned int, int,
			struct object **, unsigned char *);
#define CHECK(x) do { if (!(x)) { fprintf(stderr, "line %d: %s\n", __LINE__, #x); return 1; } } while (0)

static int refuse(struct object *self, const struct vr *caller_context)
{
	(void)self;
	(void)caller_context;
	return RN_INVALIDARG;
}

static void release(struct object *object, int dynamic)
{
	struct em_neoioic *root = get_base_members(object, MSN_NEOIOIC);
	free(root->iq.data);
	free(root->oq.data);
	if (dynamic)
		free(object);
}

int main(void)
{
	const unsigned short models[] = { MSN_AMPHICAR, MSN_CAR, MSN_VEHICLE, MSN_NEOIOIC, MSN_SHIP };
	const unsigned short seats[] = { 1, 2, 3, 4, 2 };
	struct object *object = NULL;
	uint64_t oid = OID_;
	struct vr caller = { OID_MAIN, OID_MAIN };
	union { max_align_t alignment; unsigned char bytes[65536]; } external;
	struct em_neoioic *root;
	float value;
	unsigned int quantity;
	size_t i, offset = SIZE_MAX;
	CHECK(!openoicc_reserve(&offset, 1, 2, 8, &i));
	offset = 0;
	CHECK(!openoicc_reserve(&offset, SIZE_MAX, 2, 1, &i));
	CHECK(RP(crt_amphicar(&oid, 16, 17, 2, &object, NULL)));
	CHECK(object && object->node_count == 5 && test_live == 3);
	CHECK(object->direct_bases[0]->model_id == MSN_CAR);
	CHECK(object->direct_bases[1]->model_id == MSN_SHIP);
	for (i = 0; i < 5; i++) {
		struct object *node = object->nodes + i;
		CHECK(node->model_id == models[i] && node->caller_count == seats[i] * 2);
		CHECK(node->nodes == object && node->node_count == 5);
		CHECK(!node->members || (uintptr_t)node->members % _Alignof(struct object) == 0);
		CHECK(node->open && node->input && node->output && node->io_put &&
		      node->interact0 && node->interact1 && node->interact2 && node->interact3 && node->close);
	}
	root = get_base_members(object, MSN_NEOIOIC);
	CHECK(root->iq.capacity == 16 && root->oq.capacity == 17);
	CHECK(!root->iq.front && !root->iq.rear && !root->oq.front && !root->oq.rear);
	CHECK(RP(vo_open(object, &caller)));
	for (i = 0; i < 5; i++)
		CHECK(object->nodes[i].ref_count == 1);
	CHECK(RP(vo_interact1(object, GET_TMAXVELOCITY, (unsigned char *)&value, sizeof(value), &quantity, &caller)));
	CHECK(quantity == sizeof(value) && value == 215.0f);
	CHECK(RP(vo_close(object, &caller)));
	for (i = 0; i < 5; i++) {
		CHECK(!object->nodes[i].ref_count);
		for (size_t j = 0; j < object->nodes[i].caller_count; j++)
			CHECK(!object->nodes[i].callers[j].cr);
	}
	int (*ship_close)(struct object *, const struct vr *) = object->nodes[4].close;
	int (*ship_open)(struct object *, const struct vr *) = object->nodes[4].open;
	int (*car_close)(struct object *, const struct vr *) = object->nodes[1].close;
	CHECK(RP(vo_open(object, &caller)));
	object->nodes[4].close = refuse;
	CHECK(vo_close(object, &caller) == RN_CLOSEPARTIAL);
	CHECK(object->ref_count == 1 && object->nodes[1].ref_count == 0);
	object->nodes[4].close = ship_close;
	CHECK(RP(vo_close(object, &caller)));
	object->nodes[4].open = refuse;
	CHECK(RN(vo_open(object, &caller)));
	for (i = 0; i < 5; i++)
		CHECK(!object->nodes[i].ref_count);
	object->nodes[1].close = refuse;
	CHECK(vo_open(object, &caller) == RN_CLOSEPARTIAL);
	object->nodes[4].open = ship_open;
	object->nodes[1].close = car_close;
	CHECK(RP(vo_close(object, &caller)));
	for (i = 0; i < 5; i++)
		CHECK(!object->nodes[i].ref_count);
	release(object, 1);
	CHECK(!test_live);
	for (int fail = 1; fail <= 3; fail++) {
		test_calls = 0;
		test_fail_at = fail;
		oid = OID_;
		object = (struct object *)(uintptr_t)1;
		CHECK(RN(crt_amphicar(&oid, 4, 4, 1, &object, NULL)));
		CHECK(!object && !test_live && oid == OID_);
	}
	test_fail_at = 0;
	CHECK(RN(crt_amphicar(NULL, 0, 0, 1, &object, NULL)));
	CHECK(RN(crt_amphicar(&oid, 0, 0, 0, &object, NULL)));
	CHECK(RN(crt_amphicar(&oid, 0, 0, 1, NULL, NULL)));
	CHECK(RN(crt_amphicar(&oid, 0, 0, 1, &object, external.bytes)));
	CHECK(RN(crt_amphicar(&oid, 0, 0, USHRT_MAX / 4 + 1, &object, NULL)));
	oid = OID_ | UINT16_MAX;
	CHECK(crt_amphicar(&oid, 0, 0, 1, &object, NULL) == RN_LACKOID);
	CHECK(!object);
	oid = OID_;
	CHECK(RP(crt_amphicar(&oid, 0, 0, USHRT_MAX / 4, &object, NULL)));
	CHECK(object->nodes[3].caller_count == (USHRT_MAX / 4) * 4);
	root = get_base_members(object, MSN_NEOIOIC);
	CHECK(!root->iq.data && !root->oq.data);
	release(object, 1);
	memset(external.bytes, 0xa5, sizeof(external.bytes));
	CHECK(RP(crt_amphicar(&oid, 4, 5, 1, NULL, external.bytes)));
	object = (struct object *)external.bytes;
	CHECK(!object->ref_count && test_live == 2);
	CHECK(RP(vo_open(object, &caller)) && RP(vo_close(object, &caller)));
	release(object, 0);
	CHECK(!test_live);
	for (int fail = 1; fail <= 2; fail++) {
		test_calls = 0;
		test_fail_at = fail;
		oid = OID_;
		CHECK(RN(crt_amphicar(&oid, 4, 4, 1, NULL, external.bytes)));
		CHECK(!test_live && oid == OID_ && !((struct object *)external.bytes)->oid);
	}
	puts("generated runtime checks passed");
	return 0;
}
