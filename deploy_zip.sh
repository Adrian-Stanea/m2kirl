#!/bin/bash

SCOPY_DECODER_LOCATION=/var/lib/flatpak/app/org.adi.Scopy/arm/master/2eb23ee2c0bbd73478c4c8d7720ae584df8332dbf94a4e2ee5d4a9dfbf36b935/files/share/libsigrokdecode/decoders/
SIGROK_CLI_DECODER_LOCATION=/usr/local/share/libsigrokdecode/decoders/
WORKDIR=/home/analog/m2kirl
ZIPFILE=/home/analog/m2kirl.zip
SRCDIR=/home/analog/tmp

tar xvf $ZIPFILE

echo -- creating working dir
mkdir -p $WORKDIR
cp -R $SRCDIR/m2kirl-src/* $WORKDIR/

echo -- uninstalling sigrok-cli libsigrokdecode
sudo apt-get -y remove libsigrokdecode-dev sigrok-cli

echo -- copying devicetree
sudo cp $WORKDIR/dt/config.txt /boot/
sudo cp $WORKDIR/dt/rpi-ad5592r-m2kirl.dtbo /boot/overlays

echo -- installing libm2k
cd $SRCDIR/libm2k/build
sudo make install
echo -- installing pyadi-iio
cd $SRCDIR/pyadi-iio
pip3 install .
echo -- installing libsigrokdecode
cd $SRCDIR/libsigrokdecode
sudo make install
echo -- installing sigrok-cli
cd $SRCDIR/sigrok-cli
sudo make install


echo -- copying decoder to scopy
sudo cp -R $WORKDIR/decoder/ad5592r $SCOPY_DECODER_LOCATION

echo -- copying decoder to sigrok-cli
sudo cp -R $WORKDIR/decoder/ad5592r $SIGROK_CLI_DECODER_LOCATION

echo -- setting default keyboard to US
sudo cp $WORKDIR/res/keyboard /etc/default/

