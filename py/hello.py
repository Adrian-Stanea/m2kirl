#!/bin/python3

# Simple example - turns on the green LED and then reads analog input

import libm2k
import adi

def red(ad):
    ad.voltage2_dac.raw=4095
    ad.voltage3_dac.raw=0
    
def green(ad):
    ad.voltage3_dac.raw=4095
    ad.voltage2_dac.raw=0
    
def stop_led(ad):
    ad.voltage3_dac.raw=0
    ad.voltage2_dac.raw=0
    

buffer_size = 4000
m2k_uri = "ip:192.168.2.1"
ad5592r_uri = "ip:127.0.0.1"

print("Get m2k and ad5592r handles")
ad=adi.ad5592r(ad5592r_uri)
m2k=libm2k.m2kOpen(m2k_uri)

stop_led(ad)
# m2k.calibrate()

print("Get analog-in and triggering")
ain=m2k.getAnalogIn()
trig=ain.getTrigger()

print("Setup analog-in")
ain.setSampleRate(10000000)
ain.setRange(0, -2.5, 2.5)
ain.setRange(1, -2.5, 2.5)
ain.enableChannel(0,True)
ain.enableChannel(1,True)

print("Setup analog-in triggering")
trig.reset()
green(ad) #  Turning on GREEN LED

voltage = ain.getVoltage(0)
print(voltage)
data = ain.getSamples(buffer_size)
ch0_data = data[0]
print(ch0_data) 

libm2k.contextClose(m2k)
