/* SPDX-License-Identifier: MIT */
#ifndef _WIN32
#define _POSIX_C_SOURCE 200809L
#endif
#include "text.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdarg.h>
#include <sys/stat.h>
#ifdef _WIN32
#include <windows.h>
#include <io.h>
#define get_process_id _getpid
#include <process.h>
#else
#include <unistd.h>
#define get_process_id getpid
#endif

int text_append(struct text *text, const void *data, size_t length)
{
	size_t needed;
	char *grown;
	if (length >= SIZE_MAX - text->length)
		return 0;
	needed = text->length + length + 1;
	if (needed > text->capacity) {
		size_t capacity = needed <= SIZE_MAX / 2 ? needed * 2 : needed;
		grown = realloc(text->data, capacity);
		if (!grown)
			return 0;
		text->data = grown;
		text->capacity = capacity;
	}
	memcpy(text->data + text->length, data, length);
	text->length += length;
	text->data[text->length] = 0;
	return 1;
}

int text_printf(struct text *text, const char *format, ...)
{
	va_list args, copy;
	int length;
	char *buffer;
	va_start(args, format);
	va_copy(copy, args);
	length = vsnprintf(NULL, 0, format, copy);
	va_end(copy);
	if (length < 0) {
		va_end(args);
		return 0;
	}
	buffer = malloc((size_t)length + 1);
	if (!buffer) {
		va_end(args);
		return 0;
	}
	vsnprintf(buffer, (size_t)length + 1, format, args);
	va_end(args);
	length = text_append(text, buffer, (size_t)length);
	free(buffer);
	return length;
}

int file_regular(const char *path)
{
	struct stat info;
	if (stat(path, &info))
		return 0;
#ifdef _WIN32
	DWORD attributes = GetFileAttributesA(path);
	if (attributes == INVALID_FILE_ATTRIBUTES ||
	    (attributes & FILE_ATTRIBUTE_REPARSE_POINT))
		return 0;
#else
	struct stat link_info;
	if (lstat(path, &link_info) || S_ISLNK(link_info.st_mode))
		return 0;
#endif
	return (info.st_mode & S_IFMT) == S_IFREG;
}

int file_read(const char *path, struct text *text)
{
	char buffer[8192];
	size_t quantity;
	FILE *file;
	int ok = 1;
	if (!file_regular(path))
		return 0;
	file = fopen(path, "rb");
	if (!file)
		return 0;
	while ((quantity = fread(buffer, 1, sizeof(buffer), file))) {
		if (!text_append(text, buffer, quantity)) {
			ok = 0;
			break;
		}
	}
	if (ferror(file))
		ok = 0;
	if (fclose(file))
		ok = 0;
	return ok && text_append(text, "", 0);
}

int file_prepare(const char *path, const struct text *text, char **temporary)
{
	static unsigned int serial;
	struct text name = { 0 };
	FILE *file;
	int ok;
	if (!text_printf(&name, "%s.openoicc-%lu-%u.tmp", path,
			 (unsigned long)get_process_id(), serial++))
		return 0;
	file = fopen(name.data, "wbx");
	if (!file) {
		free(name.data);
		return 0;
	}
	ok = fwrite(text->data, 1, text->length, file) == text->length;
	if (fflush(file))
		ok = 0;
#ifdef _WIN32
	if (_commit(_fileno(file)))
		ok = 0;
#else
	if (fsync(fileno(file)))
		ok = 0;
#endif
	if (fclose(file))
		ok = 0;
	if (!ok) {
		remove(name.data);
		free(name.data);
		return 0;
	}
	*temporary = name.data;
	return 1;
}

int file_commit(const char *path, const char *temporary, int replace)
{
#ifdef _WIN32
	return MoveFileExA(temporary, path, MOVEFILE_WRITE_THROUGH |
			  (replace ? MOVEFILE_REPLACE_EXISTING : 0)) != 0;
#else
	struct stat info;
	if (replace) {
		if (stat(path, &info) || chmod(temporary, info.st_mode & 0777))
			return 0;
		return rename(temporary, path) == 0;
	}
	if (link(temporary, path))
		return 0;
	return unlink(temporary) == 0;
#endif
}
