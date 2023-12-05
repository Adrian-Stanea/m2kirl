#!/bin/python3

# Based on trigger.py
# Example that showcases triggered capture - and plotting

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
trig.setAnalogSource(0)
trig.setAnalogCondition(0, libm2k.RISING_EDGE_ANALOG)
trig.setAnalogLevel(0, 0.5)
trig.setAnalogDelay(sample_delay)
trig.setAnalogMode(0, libm2k.ANALOG)

print("Start analog-in acquisition")
ain.startAcquisition(buffer_size)

for i in range(5):
    trig.setAnalogCondition(0, libm2k.RISING_EDGE_ANALOG) # set pos-edge triggering
    green(ad) #  Turning on GREEN LED - provide pos-edge

    # Data started acquiring at the top, but was waiting for trigger 
    # The stimulus was sent, data should be in the buffer now
    data = ain.getSamples(buffer_size) 
    
    plt.plot(data[0]) # plotting the received data - channel 0
    plt.show()
    plt.clf()
    print(str(i+1) + "/5 - pos-edge")
    trig.setAnalogCondition(0, libm2k.FALLING_EDGE_ANALOG) # set neg-edge triggering
    red(ad) # Turn the RED LED on - if green was ON, this should create a neg-edge
    data = ain.getSamples(buffer_size) # Data was still acquiring, but was waiting for the trigger
    plt.plot(data[0])
    plt.show()
    plt.clf()
    print(str(i+1) + "/5 - neg-edge")

ain.stopAcquisition()
libm2k.contextClose(m2k)
