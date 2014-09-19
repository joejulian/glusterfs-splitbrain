#!/bin/env python

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
# Copyright 2014, Joe Julian <me@joejulian.name>
#
import socket
import sys
from struct import pack,unpack

DEFAULT_SERVER_PORT=24007
GETSPEC=2
AUTH_GLUSTERFS=390039
AUTH_NULL=0

def _build_rpc_fetch_volfile(volume):
    # TODO: this could probably be done prettier with xmllib
    message = ''
    # Fragment Header
    message += pack('!LLLLLL',
            1, # XID
            0, # Message Type
            2, # RPC Version
            14398633, # GlusterFS Handshake
            2, # program_version
            GETSPEC) # procedure
    # credendials
    message += pack('!LLLLLLLL',
            AUTH_GLUSTERFS, # flavor
            24, # length
            0, # pid
            0, # uid
            0, # gid
            0, # aux_gids
            4, # unknown
            0) # lock_owner
    # verifier
    message += pack('!LL',
            AUTH_NULL, # flavor
            0) # length
    # handshake
    message += pack('!L',0) # flags
    # message_key
    message += pack('!L',len(volume)) # length
    message += volume # contents
    message += "\0"*(4-len(volume)%4)
    # gf_dict
    message += pack('!L',0x36) # dict size
    message += pack('!L',2) # number of entries
    message += pack('!L',0x0e) #first string length
    message += pack('!L',2) # second string length
    message += 'max-op-version'
    message += "\0"
    message += '30600'
    message += "\0"
    message += pack('!L',0x0e)
    message += pack('!L',2)
    message += 'min-op-version'
    message += "\0"
    message += '1'
    message += "\0"
    message += "\0\0" # pad the dict to the qword length
    message = pack('!L',0x80000000 | len(message)) + message # Last Fragment: Yes, Length
    return message

def fetch_volfile(server, volume, server_port = DEFAULT_SERVER_PORT):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    port = 1
    while port < 1025:
        try:
            s.bind(('0.0.0.0',port))
            break
        except:
            port += 1

    s.connect((server, server_port))
    s.send(_build_rpc_fetch_volfile(volume))
    vollen = (unpack('!L',s.recv(4))[0] & 0x7FFFFFFF) - 40
    s.recv(36) # So far, I haven't seen a need for these remaining bytes for this operation
    volfile = ''
    while len(volfile) < vollen:
        volfile += s.recv(min(1024,vollen - len(volfile)))
    s.close()
    return volfile.strip("\0")

if __name__ == '__main__':
    if len(sys.argv) <> 3:
        print 'Usage: %{0} {volfile server} {volume}'.format(sys.argv[0])
        print
        print "\tRetrieve the volfile for {volume} from {volfile server}"
        exit(1)

    print fetch_volfile(sys.argv[1], sys.argv[2])
