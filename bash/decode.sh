sigrok-cli -i - -I binary:numchannels=16:samplerate=10mhz -C 0=mosi,1=miso,2=clk,3=cs -P spi:miso=miso:mosi=mosi:clk=clk:cs=cs:cs_polarity=active-low:cpol=1:cpha=0,ad5592r
