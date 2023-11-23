├── 2.2V_oversampling.csv  - CSV file 2.2V
├── 2.2V_oversampling.sh   - script to push 2.2V
├── 2.5V.csv  - CSV file for 2.5V
├── ad5592r-boot.bin  - binary file - contains SPI capture of boot process
├── ad5592r-boot-ch3-dac.bin - binary file - contains SPI capture of boot process + setting channel 3 DAC
├── blinkfast.sh - script that blink LED without pause
├── blink.sh - script that blinks LED with 1 sec pause
├── capture_msg.sh - helper script to capture SPI messages
├── capture.sh - script that captures digital interface to STDIN
├── config-spi.sh - m2kcli spi script that configures the ad5592r as in boot process
├── decode.sh - script to decode binary files
├── green.bin - binary file containing setting the green LED
├── green.sh - script file that sets the green LED via iio_attr
├── green-spi.sh - m2kcli spi script that sets the green LED - standalone config
├── play-spi.sh - configures and blinks using m2kcli spi script - standalone config
├── red.bin - binary file containing setting the red LED
├── red.sh - script file that sets the red LED via iio_attr
├── red-spi.sh - m2kcli spi script that sets the red LED - standalone config
├── replay_demo.sh - script file that replays binary files into the ad5592r - standalone config
├── replay.sh - script file that replays binary files into the ad5592r
├── stair_step.csv - csv containing stair-step
├── stair_step.sh - script that starts the stairstep on the DAC
├── stop.bin - binary file containing commands for turning the DAC off 
└── stop.sh - script file that turns the LEDs off via iio_attr


