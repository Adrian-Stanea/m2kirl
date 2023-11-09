#!/bin/bash

m2kcli analog-out ip:192.168.2.1 --set-channel channel=0 sampling_frequency=75000000
m2kcli analog-out ip:192.168.2.1 --set-channel channel=0 oversampling_ratio=32
m2kcli analog-out ip:192.168.2.1 --generate channel=0 cyclic=1 format=csv  raw=0 buffer_size=4 < 2.2V_oversampling.csv
