#!/bin/bash
URI=$(cat uri)
if [ -z $URI ]; then
URI="ip:192.168.2.1"
fi
echo $URI


m2kcli power-supply $URI -9 channel=0 value=0
sleep 0.1
m2kcli power-supply $URI -9 channel=0 value=3.3

./config-spi.sh
while true 
do
	./red-spi.sh
	sleep 0.1
	./green-spi.sh
	sleep 0.1
done
