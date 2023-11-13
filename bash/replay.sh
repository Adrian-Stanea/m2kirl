#!/bin/bash

URI=ip:192.168.2.1

m2kcli digital $URI --set sampling_frequency_out=200000
m2kcli digital $URI -9 channel=0,1,2,3 cyclic=0 buffer_size=10000 nb_samples=10000 format=binary < $1
