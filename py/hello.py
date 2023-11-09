#!/bin/python3

import libm2k
import adi
import matplotlib.pyplot as plt
import time

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
sample_delay = -1000

m2k_uri = "ip:192.168.2.1"
ad5592r_uri = "ip:127.0.0.1"

ad=adi.ad5592r(ad5592r_uri)
m2k=libm2k.m2kOpen(m2k_uri)

stop_led(ad)
# m2k.calibrate()

ain=m2k.getAnalogIn()
trig=ain.getTrigger()

ain.setSampleRate(10000000)
ain.setRange(0, -2.5, 2.5)
ain.setRange(1, -2.5, 2.5)
ain.enableChannel(0,True)
ain.enableChannel(1,True)

trig.reset()
trig.setAnalogSource(0)
trig.setAnalogCondition(0, libm2k.RISING_EDGE_ANALOG)
trig.setAnalogLevel(0, 0.5)
trig.setAnalogDelay(sample_delay)
trig.setAnalogMode(0, libm2k.ANALOG)



print("A")
ain.startAcquisition(buffer_size)

for i in range(5):
    trig.setAnalogCondition(0, libm2k.RISING_EDGE_ANALOG)
    green(ad)
    data = ain.getSamples(buffer_size)[0]
    plt.plot(data)
    plt.show()
    plt.clf()

    trig.setAnalogCondition(0, libm2k.FALLING_EDGE_ANALOG)
    red(ad)
    data = ain.getSamples(buffer_size)[0]
    plt.plot(data)
    plt.show()
    plt.clf()

