#!/bin/bash
iio_attr -u ip:127.0.0.1 -q -c ad5592r -o voltage3 raw 4095
echo voltage3 - 4095
#m2kcli analog-in ip:192.168.2.1 -v channel=0 raw=0
iio_attr -u ip:127.0.0.1 -q -c ad5592r -o voltage2 raw 0
echo voltage2 0
#m2kcli analog-in ip:192.168.2.1 -v channel=0 raw=0
