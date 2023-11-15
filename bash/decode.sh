#JSON_FMT="--protocol-decoder-jsontrace"
#ANNOTATION="--protocol-decoder-ann-class"
#SAMPLE_NUM="--protocol-decoder-samplenum"
FILTER="-A spi=mosi-transfer,spi=miso-transfer,ad5592r"

sigrok-cli -i - $JSON_FMT $ANNOTATION $SAMPLE_NUM -I binary:numchannels=16:samplerate=10mhz -C 0=mosi,1=miso,2=clk,3=cs -P spi:miso=miso:mosi=mosi:clk=clk:cs=cs:cs_polarity=active-low:cpol=1:cpha=0,ad5592r $FILTER
