#!/usr/bin/python
# This file is part of glusterfs-splitbrain
#
# glusterfs-splitbrain is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# glusterfs-splitbrain is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with glusterfs-splitbrain. If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2014,2015 Joe Julian <me@joejulian.name>
# Copyright (c) 2012-2014 Red Hat, Inc.
#


import ctypes
import ctypes.util
import subprocess

def cli_get_volfile (host, volume):
    res = subprocess.check_output(["/usr/sbin/gluster","--remote-host={}".format(host),
        "system","getspec",volume])
    return res

def api_get_volfile (host, volume):
    # This is set to a large value to exercise the "buffer not big enough"
    # path.  More realistically, you'd just start with a huge buffer.
    BUF_LEN = 0
    fs = api.glfs_new(volume)
    #api.glfs_set_logging(fs,"/dev/stderr",7)
    api.glfs_set_volfile_server(fs,"tcp",host,24007)
    api.glfs_init(fs)
    vbuf = ctypes.create_string_buffer(BUF_LEN)
    vlen = api.glfs_get_volfile(fs,vbuf,BUF_LEN)
    if vlen < 0:
        vlen = BUF_LEN - vlen
        vbuf = ctypes.create_string_buffer(vlen)
        vlen = api.glfs_get_volfile(fs,vbuf,vlen)
    api.glfs_fini(fs)
    if vlen <= 0:
        return vlen
    return vbuf.value[:vlen]

api = ctypes.CDLL(ctypes.util.find_library("gfapi"))
try:
    api.glfs_get_volfile.argtypes = [ctypes.c_void_p,
                                     ctypes.c_void_p,
                                     ctypes.c_ulong]
    api.glfs_get_volfile.restype = ctypes.c_long;
    get_volfile = api_get_volfile
except:
    get_volfile = cli_get_volfile

if __name__ == "__main__":
    import sys

    try:
        res = apply(get_volfile,sys.argv[1:3])
    except:
        print "fetching volfile failed (volume not started?)"
        raise

    try:
        for line in res.split('\n'):
            print line
    except:
        print "bad return value %s" % res
        raise
