#!/bin/python3

# Continous acquisition according to some steps
# plots digital and analog waveforms
# decodes data in the process

import libm2k
import adi
import matplotlib.pyplot as plt
import numpy as np
import subprocess
import sys

buffer_size = 4000
sample_delay = -1000
out_oversampling = 75
spi_test_val = 3987
#show_plot = True
show_plot = False
show_decode = False
#show_decode = True
decode_sh = "../bash/decode.sh"

m2k_uri = "ip:192.168.2.1"
ad5592r_uri = "ip:127.0.0.1"

def voltage4(ad):
    return ad.voltage4_adc.raw * (ad.voltage4_adc.scale / 1000.0)

def voltage3_w(ad, val):
    ad.voltage3_dac.raw  = clamp((val / ad.voltage3_dac.scale * 1000),0,4095)
    
def voltage3_r(ad):
    return ad.voltage3_adc.raw * (ad.voltage3_adc.scale / 1000.0)

def voltage2_w(ad, val):
    ad.voltage2_dac.raw = clamp(val / ad.voltage2_dac.scale * 1000.0, 0, 4095)
    
def voltage2_r(ad):
    return ad.voltage2_adc.raw * (ad.voltage2_adc.scale / 1000.0)

_result_overall="OK"

def verify_range(val, th):
    global _result_overall
    if val <= th+0.1 and val >= th-0.1:
        return "OK"
    _result_overall = "NOK"
    return "NOK";

def verify_string_occurence(data, st):
    global _result_overall
    ret = data.find(st)
    if ret == -1:
        _result_overall = "NOK"
        return "NOK"
    return "OK"

    

def clamp(val , min, max):
    if val < min:
        return min
    if val > max:
        return max
    return val

def demux_digital_channels(digital_data):
    
    arr = []
    for i in range(16):
        bit = [((val & (1<<i)) >> i) for val in digital_data]
        arr.append(np.array(bit))
    return arr

ad=adi.ad5592r(ad5592r_uri)
m2k=libm2k.m2kOpen(m2k_uri)

# m2k.calibrate()

aout=m2k.getAnalogOut()
ain=m2k.getAnalogIn()
dig=m2k.getDigital()
trig=ain.getTrigger()

aout.setCyclic(0,True)
aout.setSampleRate(0,75000000)
aout.setOversamplingRatio(0, out_oversampling)
aout.enableChannel(0, True)

ain.setSampleRate(10000000)
ain.setRange(0, -2.5, 2.5)
ain.setRange(1, -2.5, 2.5)
ain.enableChannel(0,True)
ain.enableChannel(1,True)

dig.setSampleRateIn(10000000)
# channels are set to input by default
trig.reset()


######
# SETUP AD5592R SIGNAL
######
voltage2_w(ad,0) # reset voltage to 0
voltage3_w(ad,0) # reset voltage to 0

#####
## START STAIR STEP
#####
outbuf = [0] * 10 + [0.5]*10 + [1]*10 + [1.5]*10
aout.enableChannel(0, True)
aout.push(0,outbuf)

#####
## SETUP MIXED SIGNAL MODE
#####
print("STATUS - SETUP MIXED SIGNAL ACQUISITION")

trig.setAnalogDelay(sample_delay)
trig.setAnalogSource(libm2k.SRC_DIGITAL_IN)
trig.setAnalogMode(0, libm2k.ANALOG)
trig.setDigitalDelay(sample_delay)
trig.setDigitalSource(libm2k.SRC_NONE)
trig.setDigitalCondition(0, libm2k.NO_TRIGGER_DIGITAL)
trig.setDigitalCondition(1, libm2k.NO_TRIGGER_DIGITAL)
trig.setDigitalCondition(2, libm2k.NO_TRIGGER_DIGITAL)
trig.setDigitalCondition(3, libm2k.FALLING_EDGE_DIGITAL)

steps = [{"cmd":"voltage2_w(ad,0)", "description":"OFF - BOTH 0V"},
         {"cmd":"voltage3_w(ad,2.5)", "description":"WRITE V3 GREEN LED ON"},
         {"cmd":"voltage3_r(ad)","description":"READ VOLTAGE3"},
         {"cmd":"voltage2_w(ad,2.5)","description":"OFF - BOTH 2.5V"},
         {"cmd":"voltage3_w(ad,0)","description":"RED LED ON"},
         {"cmd":"voltage3_r(ad)","description":"READ VOLTAGE 3"}
         ]
idx = 0
while 1:
    idx = idx + 1
    if idx == len(steps):
        idx = 0
    print("STATUS - STARTED MIXED SIGNAL ACQUISITION")
    m2k.startMixedSignalAcquisition(buffer_size)

    #####
    # STIMULUS
    #####
    eval(steps[idx]["cmd"])


    #####
    # Get Samples from M2k
    #####
    analog_data = ain.getSamples(buffer_size) # GET SAMPLES FROM M2k
    digital_data = dig.getSamples(buffer_size) # GET SAMPLES FROM M2k
    m2k.stopMixedSignalAcquisition()

    #convert data from ints to bytes
    data = np.array(digital_data,dtype='<u2').tobytes()
    proc = subprocess.run(["/bin/bash",decode_sh], input=data,  capture_output=True)
    decoded_data = proc.stdout.decode()
    print(decoded_data)

    #####
    # pretty plotting
    ######

    plt.clf()
    processed_digital_data = demux_digital_channels(digital_data)
    plt.title(steps[idx]["description"])
    plt.plot(analog_data[0])
    plt.plot(analog_data[1])
    plot_offset = 6
    plot_spacing = 1.2
    for ch in [0,1,2,3]:
        plt.plot(processed_digital_data[ch] + plot_spacing * ch + plot_offset)
    plt.show(block=False)
    plt.pause(0.5)



#####
# CLEANUP
#####
print("STATUS - CLEANUP")
print("TEST RESULT - ", _result_overall)
if(_result_overall == "NOK"):
    print("Check calibration, check GND, check connections")

aout.stop()
trig.reset()
libm2k.contextClose(m2k)
