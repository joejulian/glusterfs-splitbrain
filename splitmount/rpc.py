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
import os
import subprocess
import sys

# Monkeypatch subprocess for 2.6
if sys.version_info[:2] == (2,6):
    try:
        from subprocess import STDOUT, check_output, CalledProcessError
    except ImportError:  # pragma: no cover
        # python 2.6 doesn't include check_output
        # monkey patch it in!
        import subprocess
        STDOUT = subprocess.STDOUT

        def check_output(*popenargs, **kwargs):
            if 'stdout' in kwargs:  # pragma: no cover
                raise ValueError('stdout argument not allowed, '
                                 'it will be overridden.')
            process = subprocess.Popen(stdout=subprocess.PIPE,
                                       *popenargs, **kwargs)
            output, _ = process.communicate()
            retcode = process.poll()
            if retcode:
                cmd = kwargs.get("args")
                if cmd is None:
                    cmd = popenargs[0]
                raise subprocess.CalledProcessError(retcode, cmd,
                                                    output=output)
            return output
        subprocess.check_output = check_output

        # overwrite CalledProcessError due to `output`
        # keyword not being available (in 2.6)
        class CalledProcessError(Exception):

            def __init__(self, returncode, cmd, output=None):
                self.returncode = returncode
                self.cmd = cmd
                self.output = output

            def __str__(self):
                return "Command '%s' returned non-zero exit status %d" % (
                    self.cmd, self.returncode)
        subprocess.CalledProcessError = CalledProcessError

def cli_get_volfile (host, volume):
    res = subprocess.check_output(["/usr/sbin/gluster","--remote-host={0}".format(host),
        "system","getspec",volume])
    return res

def api_get_volfile (host, volume):
    # This is set to a large value to exercise the "buffer not big enough"
    # path.  More realistically, you'd just start with a huge buffer.
    BUF_LEN = 0
    logfile = str.encode(os.path.join(os.getcwd(),"gfapi.log"))
    loglevel = 7 #debug
    fs = api.glfs_new(str.encode(volume))
    api.glfs_set_logging(fs, logfile, loglevel)
    api.glfs_set_volfile_server(fs, str.encode("tcp"), str.encode(host),24007)
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
    api.glfs_new.argtypes=[ctypes.c_char_p]
    api.glfs_new.restype = ctypes.c_void_p
    api.glfs_set_logging.argtypes=[ctypes.c_void_p,
                                   ctypes.c_char_p,
                                   ctypes.c_int]
    api.glfs_set_logging.restype = ctypes.c_int
    api.glfs_get_volfile.argtypes = [ctypes.c_void_p,
                                     ctypes.c_void_p,
                                     ctypes.c_ulong]
    api.glfs_get_volfile.restype = ctypes.c_long
    get_volfile = api_get_volfile
    api.glfs_set_volfile_server.argtypes = [ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_int]
    api.glfs_set_volfile_server.restype = ctypes.c_int
    api.glfs_init.argtypes = [ctypes.c_void_p]
    api.glfs_init.restype = ctypes.c_int
    api.glfs_fini.argtypes = [ctypes.c_void_p]
    api.glfs_fini.restype = ctypes.c_int


except:
    get_volfile = cli_get_volfile

if __name__ == "__main__":
    import sys

    try:
        res = get_volfile(*sys.argv[1:3]).decode('utf-8')
    except:
        print("Fetching volfile failed for volume {1} on server {0}. See gfapi.log.".format(*sys.argv[1:3]))
        exit(1)

    try:
        for line in res.split(u'\n'):
            print(line)
    except:
        print("bad return value {0}".format(res))
        raise
