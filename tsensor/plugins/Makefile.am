#
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# auto makefile for the nprobe plugins.
# (this file is processed with 'automake' to produce Makefile.in)
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#

SUBDIRS = . 

PLUGIN_DIST_COMMON = Makefile.am Makefile.in
DISTCLEANFILES =  \#* *~ *.log *.o
CLEANFILES     = $(DISTCLEANFILES)
EXTRA_DIST  =
LDFLAGS = -pthread

SUFFIXES    = .so

# 
# Where to install the plugin 
# 
plugindir = ${exec_prefix}/lib/lyprobe/plugins
libdir = $(plugindir)

INCLUDES = -I.. @INCS@ 

.NOTPARALLEL:

#
# nProbe's meat
#

noinst_PROGRAMS = \
									httpPlugin.so \
									l7Plugin.so \
									dnsPlugin.so \
									servicePlugin.so \
									icmpPlugin.so 

lib_LTLIBRARIES = \
									libhttpPlugin.la \
									libl7Plugin.la \
									libdnsPlugin.la \
									libservicePlugin.la \
									libicmpPlugin.la 

######################################################

libicmpPlugin_la_SOURCES = icmpPlugin.c
libicmpPlugin_la_LDFLAGS = -shared -release @PACKAGE_VERSION@ @DYN_FLAGS@
libicmpPlugin_la_CFLAGS = $(AM_CFLAGS)

.libs/libicmpPlugin.so@SO_VERSION_PATCH@:
	@if test -f libicmpPlugin_la-icmpPlugin.o; then \
		$(CC) @MAKE_SHARED_LIBRARY_PARM@ -o .libs/libicmpPlugin.so@SO_VERSION_PATCH@ libicmpPlugin_la-icmpPlugin.o; \
		else \
		$(CC) @MAKE_SHARED_LIBRARY_PARM@ -o .libs/libicmpPlugin.so@SO_VERSION_PATCH@ icmpPlugin.o; \
		fi

icmpPlugin.so$(EXEEXT): .libs/libicmpPlugin.so@SO_VERSION_PATCH@
	@$(LN_S) .libs/libicmpPlugin.so icmpPlugin.so$(EXEEXT)

######################################################

libservicePlugin_la_SOURCES = servicePlugin.c cJSON.c
libservicePlugin_la_LDFLAGS = -shared -release @PACKAGE_VERSION@ @DYN_FLAGS@ 
libservicePlugin_la_CFLAGS = $(AM_CFLAGS)

.libs/libservicePlugin.so@SO_VERSION_PATCH@:
	@if test -f libservicePlugin_la-servicePlugin.o; then \
		$(CC) @MAKE_SHARED_LIBRARY_PARM@ -o .libs/libservicePlugin.so@SO_VERSION_PATCH@ libservicePlugin_la-servicePlugin.o cJSON.o; \
		else \
		$(CC) @MAKE_SHARED_LIBRARY_PARM@ -o .libs/libservicePlugin.so@SO_VERSION_PATCH@ servicePlugin.o cJSON.o; \
		fi

servicePlugin.so$(EXEEXT): .libs/libservicePlugin.so@SO_VERSION_PATCH@
	@$(LN_S) .libs/libservicePlugin.so servicePlugin.so$(EXEEXT)

######################################################

libl7Plugin_la_SOURCES = l7Plugin.c
libl7Plugin_la_LDFLAGS = -shared -release @PACKAGE_VERSION@ @DYN_FLAGS@
libl7Plugin_la_CFLAGS = $(AM_CFLAGS)

.libs/libl7Plugin.so@SO_VERSION_PATCH@:
	@if test -f libl7Plugin_la-l7Plugin.o; then \
		$(CC) @MAKE_SHARED_LIBRARY_PARM@ -o .libs/libl7Plugin.so@SO_VERSION_PATCH@ libl7Plugin_la-l7Plugin.o; \
		else \
		$(CC) @MAKE_SHARED_LIBRARY_PARM@ -o .libs/libl7Plugin.so@SO_VERSION_PATCH@ l7Plugin.o; \
		fi

l7Plugin.so$(EXEEXT): .libs/libl7Plugin.so@SO_VERSION_PATCH@
	@$(LN_S) .libs/libl7Plugin.so l7Plugin.so$(EXEEXT)

######################################################

libhttpPlugin_la_SOURCES = httpPlugin.c
libhttpPlugin_la_LDFLAGS = -shared -release @PACKAGE_VERSION@ @DYN_FLAGS@
libhttpPlugin_la_CFLAGS = $(AM_CFLAGS)

.libs/libhttpPlugin.so@SO_VERSION_PATCH@:
	@if test -f libhttpPlugin_la-httpPlugin.o; then \
		$(CC) @MAKE_SHARED_LIBRARY_PARM@ -o .libs/libhttpPlugin.so@SO_VERSION_PATCH@ libhttpPlugin_la-httpPlugin.o; \
		else \
		$(CC) @MAKE_SHARED_LIBRARY_PARM@ -o .libs/libhttpPlugin.so@SO_VERSION_PATCH@ httpPlugin.o; \
		fi

httpPlugin.so$(EXEEXT): .libs/libhttpPlugin.so@SO_VERSION_PATCH@
	@$(LN_S) .libs/libhttpPlugin.so httpPlugin.so$(EXEEXT)

#####################################################

libdnsPlugin_la_SOURCES = dnsPlugin.c
libdnsPlugin_la_LDFLAGS = -shared -release @PACKAGE_VERSION@ @DYN_FLAGS@
libdnsPlugin_la_CFLAGS = $(AM_CFLAGS)

.libs/libdnsPlugin.so@SO_VERSION_PATCH@:
	@if test -f libdnsPlugin_la-dnsPlugin.o; then \
		$(CC) @MAKE_SHARED_LIBRARY_PARM@ -o .libs/libdnsPlugin.so@SO_VERSION_PATCH@ libdnsPlugin_la-dnsPlugin.o; \
		else \
		$(CC) @MAKE_SHARED_LIBRARY_PARM@ -o .libs/libdnsPlugin.so@SO_VERSION_PATCH@ dnsPlugin.o; \
		fi

dnsPlugin.so$(EXEEXT): .libs/libdnsPlugin.so@SO_VERSION_PATCH@
	@$(LN_S) .libs/libdnsPlugin.so dnsPlugin.so$(EXEEXT)

######################################################