#!/bin/bash
OLD_SPACK_ROOT="spacks/old-spack"
SPLICE_SPACK_ROOT="spacks/splice-spack"

BASE_CMD="git clone -c feature.manyFiles=true https://github.com/spack/spack.git"

if [ ! -d "$OLD_SPACK_ROOT" ]; then
    $BASE_CMD $OLD_SPACK_ROOT
    pushd $OLD_SPACK_ROOT
    git fetch
    git checkout "ad518d975c711c04bdc013363d8fc33a212e9194" 
    popd
fi
if [ ! -d "$SPLICE_SPACK_ROOT" ]; then
    $BASE_CMD $SPLICE_SPACK_ROOT
    pushd $SPLICE_SPACK_ROOT
    git fetch
    git checkout "9f7cff1780d1e3e97cf957d686966a74d3840af6"
    popd
fi
