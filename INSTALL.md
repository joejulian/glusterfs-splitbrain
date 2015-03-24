# splitmount Installation Guide

## Building and Installing splitmount

Download the source:

    git clone https://github.com/joejulian/glusterfs-splitbrain.git splitmount
    cd splitmount

To install _splitmount_ in your home directory:

    python setup.py install --user

To install _splitmount_ system wide:

    python setup.py install

Prior to GlusterFS 3.6.2 this tool requires the gluster cli. Post 3.6.2 it uses libgfapi. Ensure the package for your distribution is installed that provides this requirement.
