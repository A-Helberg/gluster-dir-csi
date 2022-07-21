#!/usr/bin/env bash
./build.sh && docker run --rm -ti --privileged -v "$PWD/docker-csi:/csi" ahelberg/gluster-dir-csi
