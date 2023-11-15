#!/bin/bash

M2KIRL_REPO=https://github.com/adisuciu/m2kirl 
STAGING_DIR=/home/analog/tmp
OUTPUT_ZIP=/home/analog/m2kirl.zip

LIBM2K_VER=7b31a3d
PYADI_VER=8bcfac1
SIGROKDECODE_VER=0c35c5c
SIGROKCLI_VER=9d9f7b8

echo -- cloning m2kirl
mkdir -p $STAGING_DIR
cd $STAGING_DIR
git clone $M2KIRL_REPO m2kirl-src

echo -- installing libm2k
cd $STAGING_DIR
git clone https://github.com/analogdevicesinc/libm2k
cd libm2k
git reset --hard $LIBM2K_VER 
mkdir build && cd build
cmake -DENABLE_TOOLS=ON -DENABLE_PYTHON=ON ../
make

echo -- installing pyadi-iio
cd $STAGING_DIR
git clone https://github.com/analogdevicesinc/pyadi-iio
cd pyadi-iio
git reset --hard $PYADI_VER

echo -- installing libsigrokdecode
cd $STAGING_DIR
git clone https://github.com/sigrokproject/libsigrokdecode
cd libsigrokdecode
git reset --hard $SIGROKDECODE_VER
./autogen.sh
./configure
make

echo -- installing sigrok-cli
cd $STAGING_DIR
git clone https://github.com/sigrokproject/sigrok-cli
cd sigrok-cli
git reset --hard $SIGROKCLI_VER
./autogen.sh
./configure
make

echo -- building zip
tar -cf $OUTPUT_ZIP $STAGING_DIR


