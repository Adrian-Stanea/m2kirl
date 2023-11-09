#!/bin/bash

URI=ip:192.168.2.1

m2kcli digital $URI --set sampling_frequency_out=10000000
m2kcli digital $URI -9 channel=0,1,2,3 cyclic=0 buffer_size=5000000 format=binary < f.dat
