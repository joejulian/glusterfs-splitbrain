glusterfs-splitbrain
====================

Admin tool to aid in the recovery of split-brain file entries

Usage: splitmount {volfile server} {volume} {mount path}

This mounts the split replicas into as many directories as your replica count, maintaining
consistency among distribute subvolumes. This allows you to compare versions across replica
and remove the invalid copy from the server in order to resolve split-brain.

Example: for a 8x2 (8 brick replica 2) volume named mybrick partially hosted by server1:


    splitmount server1 mybrick /root/sb_mybrick


Would create the mount points, /root/sb_mybrick/r1 and /root/sb_mybrick/r2 with each mount containing the distribute portion of each replica, in this case 4 bricks.

From there you could remove the splitbrain file from under r1 or r2 as you see fit.


