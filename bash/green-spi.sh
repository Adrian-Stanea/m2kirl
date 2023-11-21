#!/bin/bash

URI="ip:192.168.2.1"
m2kcli spi $URI -i frequency=200000 clk=2 mosi=0 cs=3 mode=1 cs_polarity=0 bit_numbering=MSB -w data=0xa0,0x00
m2kcli spi $URI -i frequency=200000 clk=2 mosi=0 cs=3 mode=1 cs_polarity=0 bit_numbering=MSB -w data=0xbf,0xff

