 import sigrokdecode as srd
 
 class Decoder(srd.Decoder):
     api_version = 3
     id = 'i2c'
     name = 'I²C'
     longname = 'Inter-Integrated Circuit'
     desc = 'Two-wire, multi-master, serial bus.'
     license = 'gplv2+'
     inputs = ['logic']
     outputs = ['i2c']
     channels = (
         {'id': 'scl', 'name': 'SCL', 'desc': 'Serial clock line'},
         {'id': 'sda', 'name': 'SDA', 'desc': 'Serial data line'},
     )
     optional_channels = ()
     options = (
         {'id': 'address_format', 'desc': 'Displayed slave address format',
            'default': 'shifted', 'values': ('shifted', 'unshifted')},
     )
     annotations = (
         ('start', 'Start condition'),
         ('repeat-start', 'Repeat start condition'),
         ('stop', 'Stop condition'),
         ('ack', 'ACK'),
         ('nack', 'NACK'),
         ('bit', 'Data/address bit'),
         ('address-read', 'Address read'),
         ('address-write', 'Address write'),
         ('data-read', 'Data read'),
         ('data-write', 'Data write'),
         ('warnings', 'Human-readable warnings'),
     )
     annotation_rows = (
         ('bits', 'Bits', (5,)),
         ('addr-data', 'Address/Data', (0, 1, 2, 3, 4, 6, 7, 8, 9)),
         ('warnings', 'Warnings', (10,)),
     )
 
     def __init__(self, **kwargs):
         self.state = 'FIND START'
         # And various other variable initializations...
 
     def metadata(self, key, value):
         if key == srd.SRD_CONF_SAMPLERATE:
             self.samplerate = value

     def reset(self):
         #reset inner states 
 
     def start(self):
         self.out_ann = self.register(srd.OUTPUT_ANN)
 
     def decode(self):