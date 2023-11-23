#!/bin/bash
# this script captures red/stop/green messages from pi->ad5592r communication
# these can be later used with ./replay
URI=$(cat uri)
if [ -z $URI ]; then
URI="ip:192.168.2.1"
fi
echo $URI

m2kcli digital $URI --set sampling_frequency_in=10000000
m2kcli digital $URI --set-channel channel=3 trigger_condition=falling_edge
m2kcli digital $URI --set trigger_delay=-100

# 2 buffers because there are 2 transactions (nb_samples = 2xbuffer_size)
m2kcli digital $URI -c buffer_size=50000 nb_samples=100000 format=binary > stop.bin &
./stop.sh
./decode < stop.bin

m2kcli digital $URI -c buffer_size=50000 nb_samples=100000 format=binary > red.bin &
./red.sh
./decode < red.bin

m2kcli digital $URI -c buffer_size=50000 nb_samples=100000 format=binary > green.bin &
./green.sh
./decode < green.bin


