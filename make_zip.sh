#!/bin/bash

M2KIRL_REPO=https://github.com/adisuciu/m2kirl 
STAGING_DIR=/home/analog/tmp
OUTPUT_ZIP=/home/analog/m2kirl.zip

echo -- cloning m2kirl
mkdir -p $STAGING_DIR
cd $STAGING_DIR
git clone $M2KIRL_REPO m2kirl-src

echo -- installing libm2k
cd $STAGING_DIR
git clone https://github.com/analogdevicesinc/libm2k
cd libm2k
mkdir build && cd build
cmake -DENABLE_TOOLS=ON -DENABLE_PYTHON=ON ../
make

echo -- installing pyadi-iio
cd $STAGING_DIR
git clone https://github.com/analogdevicesinc/pyadi-iio

echo -- installing libsigrokdecode
cd $STAGING_DIR
git clone https://github.com/sigrokproject/libsigrokdecode
cd libsigrokdecode
./autogen.sh
./configure
make

echo -- installing sigrok-cli
cd $STAGING_DIR
git clone https://github.com/sigrokproject/sigrok-cli
cd sigrok-cli
./autogen.sh
./configure
make

echo -- building zip
tar -cf $OUTPUT_ZIP $STAGING_DIR


