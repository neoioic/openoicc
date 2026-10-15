/* SPDX-License-Identifier: MIT */
#include "host/host.h"
#include "objects/project.h"
#include <stdio.h>
#include <string.h>

static void usage(void)
{
	puts("Usage: openoicc new NAME PATH.c [BASES]\n"
	     "       openoicc check FILE.c...\n"
	     "       openoicc generate [--write] FILE.c...\n"
	     "BASES is a quoted comma-separated list (default OIOIC).\n"
	     "generate previews changes unless --write is specified.");
}

int main(int argc, char **argv)
{
	struct object *project = NULL;
	struct vr caller = { OID_OPENOICC, OID_OPENOICC };
	struct project_request request;
	int result, closed, first = 2, write = 0, exit_status;
	if (argc == 2 && (!strcmp(argv[1], "--help") || !strcmp(argv[1], "--version"))) {
		if (!strcmp(argv[1], "--version"))
			puts("OpenOICC 0.1.0");
		else
			usage();
		return 0;
	}
	if (argc >= 2 && !strcmp(argv[1], "new")) {
		if (argc != 4 && argc != 5) {
			usage();
			return 2;
		}
		return node_create(argv[2], argv[3], argc == 5 ? argv[4] : "OIOIC") ? 0 : 1;
	}
	if (argc < 3 || (strcmp(argv[1], "generate") && strcmp(argv[1], "check"))) {
		usage();
		return 2;
	}
	if (!strcmp(argv[1], "generate") && !strcmp(argv[2], "--write")) {
		write = 1;
		first++;
	}
	if (first == argc || argv[first][0] == '-') {
		usage();
		return 2;
	}
	request = (struct project_request){ argc - first, argv + first, write };
	result = create_object(MSN_PROJECT, 0, 0, 1, &project);
	if (RN(result)) {
		fputs("cannot create project object\n", stderr);
		return 1;
	}
	result = vo_open(project, &caller);
	if (RP(result))
		result = vo_interact2(project, AC2_PROJECT_RUN, (unsigned char *)&request,
				      sizeof(request), &caller);
	exit_status = RP(result) ? 0 : 1;
	/* This object's close is deterministic and owns no fallible business
	 * cleanup. A partial close is retried before any destroy operation. */
	closed = vo_close(project, &caller);
	if (closed == RN_CLOSEPARTIAL)
		closed = vo_close(project, &caller);
	if (RN(closed)) {
		fputs("project close failed; object retained for cleanup\n", stderr);
		return 1;
	}
	if (!host_destroy_object(project))
		return 1;
	free(project);
	return exit_status;
}
