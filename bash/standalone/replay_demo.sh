#!/bin/bash
URI=$(cat uri)
if [ -z $URI ]; then
URI="ip:192.168.2.1"
fi
echo $URI

# turn on adalm2000 power supply
echo -- restarting ad5592r
m2kcli power-supply $URI -9 channel=0 value=0
sleep 0..1
m2kcli power-supply $URI -9 channel=0 value=3.3
echo -- ad5592r powered on
# replay boot capture
echo -- ad5592r booting
./replay.sh < ad5592r-boot-ch3-dac.bin
# turn on GREEN LED
while true 
do
./replay.sh < stop.bin
m2kcli spi $URI -i frequency=200000 clk=2 mosi=0 cs=3 mode=1 cs_polarity=0 bit_numbering=MSB -w data=0xa0,0x00
m2kcli spi $URI -i frequency=200000 clk=2 mosi=0 cs=3 mode=1 cs_polarity=0 bit_numbering=MSB -w data=0xbf,0xff
sleep 0.1
./replay.sh < stop.bin
m2kcli spi $URI -i frequency=200000 clk=2 mosi=0 cs=3 mode=1 cs_polarity=0 bit_numbering=MSB -w data=0xb0,0x00
m2kcli spi $URI -i frequency=200000 clk=2 mosi=0 cs=3 mode=1 cs_polarity=0 bit_numbering=MSB -w data=0xaf,0xff
sleep 0.1
done
