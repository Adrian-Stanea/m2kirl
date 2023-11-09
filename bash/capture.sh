#!/bin/bash

URI=ip:192.168.2.1

m2kcli digital $URI --set sampling_frequency_in=10000000
m2kcli digital $URI --set-channel channel=3 trigger_condition=falling_edge
m2kcli digital $URI --set trigger_delay=-100
m2kcli digital $URI -c buffer_size=5000000 nb_samples=5000000 format=binary