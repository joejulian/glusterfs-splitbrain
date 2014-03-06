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
import rpc.fetchvol
import os,sys,re
import tempfile
import subprocess

def main():
    me = os.path.basename(sys.argv[0])
    if len(sys.argv) <> 4:
        print
        print 'Usage: {0} {{volfile server}} {{volume}} {{mount path}}'.format(me)
        print
        print "This mounts the split replicas into as many directories as your replica count, maintaining"
        print "consistency among distribute subvolumes. This allows you to compare versions across replica"
        print "and remove the invalid copy from the server in order to resolve split-brain."
        print
        print "Example: for a 8x2 (8 brick replica 2) volume named foo partially hosted by server1:"
        print
        print "\t{0} server1 foo /root/sb_foo".format(me)
        print
        print "Would create the mount points, /root/sb_foo/r1 and /root/sb_foo/r2."
        print "From there you could remove the splitbrain file from under r1 or r2 as you"
        print "see fit."
        print
        exit(1)

    server, volume, path = sys.argv[1:]
    if not os.path.isdir(path):
        os.makedirs(path)
    if os.path.isdir(os.path.join(path,'r1')):
        print 'Please clean that path. Ensure there is nothing mounted there and delete the contents'
        print 'of that directory, or choose another directory.'
        exit(1)

    orig_vol = rpc.fetchvol.fetch_volfile(server, volume)
    regex = re.compile(r'(^volume\s.+?end-volume)', re.VERBOSE|re.MULTILINE|re.DOTALL)
    graph = [ x.strip("\n") for x in regex.split(orig_vol) if x.strip("\n") ]
    newgraph = []
    replicas = []
    for translator in graph:
        if "cluster/replicate" in translator:
            for line in translator.split('\n'):
                if 'subvolumes' in line:
                    thesereplicas = line.strip(' ').split(' ')[1:]
                    if len(replicas) == 0:
                        replicas = thesereplicas
                    else:
                      replicas = [' '.join((x,y)) for x,y in zip(replicas, thesereplicas)]
        elif "cluster/distribute" in translator:
            distribute = []
            for line in translator.split('\n'):
                if not 'subvolumes' in line:
                    distribute.append(line)
                else:
                    distribute.append('    subvolumes {bricks}')
            newgraph.append("\n".join(distribute))
        else:
            newgraph.append(translator)

    newgraph = "\n\n".join(newgraph)
    i=1
    for replica in replicas:
        tempfd,tempname = tempfile.mkstemp(dir=path)
        thisvolfile = os.fdopen(tempfd,"w")
        thisvolfile.write(newgraph.format(bricks = replica))
        thisvolfile.close()
        os.mkdir(os.path.join(path,'r{0}'.format(i)))
        subprocess.call(["/usr/sbin/glusterfs","-f",tempname,os.path.join(path,'r{0}'.format(i))])
        i += 1
    print 'Your split replicas are mounted under {0}, in directories r1 through r{1}'.format(path,i-1)

if __name__ == '__main__':
  main()
