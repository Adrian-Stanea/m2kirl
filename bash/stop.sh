#!/bin/bash

iio_attr -u ip:127.0.0.1 -q -c ad5592r -o voltage2 raw 0
iio_attr -u ip:127.0.0.1 -q -c ad5592r -o voltage3 raw 0
