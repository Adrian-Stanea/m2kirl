def disabled_enabled(v, options=None):
    return 'Disabled' if v == 0 else 'Enabled'


def dac_ch(v, options=None):
    return 'DAC{0}'.format(v)


def adc_chn(v, options=None):
    return 'ADC{v}'.format(v=v)


def empty_str(v, options=None):
    return ''


def dec_to_hex(v, options=None):
    '''Convert a number to a string with hexadecimal representation.'''
    return '0x{0:02X}'.format(v)


def bit_indices(num, options=None):
    '''Return bit indices of a number as a string where bits are set to 1.'''
    res = []
    i = 0
    while num:
        if num & 1:
            res.append(str(i))
        num >>= 1
        i += 1
    return ','.join(res)

def raw_voltage(v, options=None):
    lsb_scale = options['v_ref'] / 4096
    volts = round(v * lsb_scale, 3)
    return '{raw}[raw], {volts}[V]'.format(raw=v, volts=volts)

def raw_temperature(v, options=None):
    v_ref = options['v_ref']
    # pg 25: AD5592R(Rev.H)
    temperature = 25 + ( v - (0.5 / v_ref) * 4095) / (2.654 / (2.5/v_ref))  
    return '{raw}[raw], {temperature}[°C]'.format(raw=v, temperature=round(temperature, 1))
    

#   CTRL_REGISTERS: dict
#       Opcode (key):  a control register
#       Value:  tuple
#          0:  register name : str    
#          1:  Field Configuration (Tuple)
#               0:  start bit    : int
#               1:  width        : int
#               2:  field name   : int
#               3:  field parser : function(field_value, decoder_options) -> str
#       
#   Special keys: 'ADDR_IDX', 'MSB_IDX' -> provide global description
CTRL_REGISTERS = {
    0b0000: (
        'NOP',
        (
            (11, 4, 'REG_ADDR', dec_to_hex),
        ),
    ),
    0b0001: (
        'DAC_RD',
        (
            (0, 3, 'DAC_CH_SEL', dac_ch),
            (3, 2, 'DAC_RD_EN', disabled_enabled),
            (5, 6, 'RESERVED', empty_str),
            (11, 4, 'REG_ADDR', dec_to_hex),
        ),
    ),
    0b0010: (
        'ADC_SEQ',
        (
            (0, 8, 'ADC Channels', bit_indices),
            # When enabled temp also sent to MISO
            (8, 1, 'Temp Indicator', disabled_enabled),
            (9, 1, 'Repeat', disabled_enabled),
            (10, 1, 'RESERVED', empty_str),
            (11, 4, 'REG_ADDR', dec_to_hex),
        )
    ),
    0b0011: (
        'GEN_CTRL_REG',
        (
            (0,  4, 'RESERVED', empty_str),
            (4,  1, 'DAC_RANGE', lambda v: '0V to {text}'.format(
                text=['Vref', '2xVref'][v])),
            (5,  1, 'ADC_RANGE', lambda v: '0V to {text}'.format(
                text=['Vref', '2xVref'][v])),
            (6,  1, 'ALL_DAC', disabled_enabled),
            (7,  1, 'IO_LOCK', disabled_enabled),
            (8,  1, 'ADC_BUF_EN', disabled_enabled),
            (9,  1, 'ADC_BUF_PRECH', disabled_enabled),
            (10, 1, 'RESERVED', empty_str),
            (11, 4, 'REG_ADDR', dec_to_hex),
        )
    ),
    0b0100: (
        'ADC_CONFIG',
        (
            (0, 8, 'ADC input pins', bit_indices),
            (8, 3, 'RESERVED', empty_str),
            (11, 4, 'REG_ADDR', dec_to_hex),
        )
    ),
    0b0101: (
        'DAC_CONFIG',
        (
            (0, 8, 'DAC output pins', bit_indices),
            (8, 3, 'RESERVED', empty_str),
            (11, 4, 'REG_ADDR', dec_to_hex),
        )
    ),
    0b0110: (
        'PULLDWN_CONFIG',
        (
            (0, 8, 'Weak-pulldown output pins', bit_indices),
            (8, 3, 'RESERVED', empty_str),
            (11, 4, 'REG_ADDR', dec_to_hex),
        )
    ),
    0b0111: (
        'CONFIG_READ_AND_LDAC',
        (
            (0, 2, 'LDAC_MODE', empty_str),
            (2, 4, 'Read back register', dec_to_hex),
            (6, 1, 'REG_RD_EN', disabled_enabled),
            (7, 4, 'REG_RD_EN', empty_str),
            (11, 4, 'REG_ADDR', dec_to_hex),
        )
    ),
    0b1000: (
        'GPIO_CONFIG',
        (
            (0, 8, 'GPIO output pins', bit_indices),
            (8, 1, 'EN_BUSY', disabled_enabled),
            (9, 2, 'RESERVED', empty_str),
            (11, 4, 'REG_ADDR', dec_to_hex),
        )
    ),
    0b1001: (
        'GPIO_OUTPUT'
    ),
    0b1010: (
        'GPIO_INPUT',
        (
            (0, 8, 'GPIO input pins', bit_indices),
            (9, 2, 'RESERVED', empty_str),
            (10, 1, 'GPIO_RD_EN', disabled_enabled),
            (11, 4, 'REG_ADDR', dec_to_hex),
        )
    ),
    0b1011: (
        'PD_REF_CTRL',
        (
            (0, 8, 'DAC power-down pins', bit_indices),
            (8, 1, 'RESERVED', empty_str),
            (9, 1, 'Internal reference', disabled_enabled),
            (10, 1, 'Power down all', disabled_enabled),
            (11, 4, 'REG_ADDR', dec_to_hex),
        )
    ),
    0b1100: (
        'GPIO_OPENDRAIN_CONFIG',
        (
            (0, 8, 'GPIO open-drain pins', bit_indices),
            (8, 3, 'RESERVED', empty_str),
            (11, 4, 'REG_ADDR', dec_to_hex),
        )
    ),
    0b1101: (
        'IO_TS_CONFIG',
        (
            (0, 8, 'Three-state output pins', bit_indices),
            (8, 3, 'RESERVED', empty_str),
            (11, 4, 'REG_ADDR', dec_to_hex),
        )
    ),
    0b1111: (
        'SW_RESET',
        (
            (0, 8, 'Reset command', dec_to_hex),
            (11, 4, 'REG_ADDR', dec_to_hex),
        )
    ),
    'ADDR_IDX': (11, 4),
    'MSB_IDX': (15, 1),
}

DAC_CHANNELS = {
    # any DAC addr write [0 to 7] has the same register structure
    0: (
        'DAC_WR',
        (
            (0, 12, 'DAC data'),
            (12, 3, 'DAC addr')
        )
    ),
    1: (
        'DAC_WR',
        (
            (0, 12, 'DAC data'),
            (12, 3, 'DAC addr')
        )
    ),
    2: (
        'DAC_WR',
        (
            (0, 12, 'DAC data'),
            (12, 3, 'DAC addr')
        )
    ),
    3: (
        'DAC_WR',
        (
            (0, 12, 'DAC data'),
            (12, 3, 'DAC addr')
        )
    ),
    4: (
        'DAC_WR',
        (
            (0, 12, 'DAC data'),
            (12, 3, 'DAC addr')
        )
    ),
    5: (
        'DAC_WR',
        (
            (0, 12, 'DAC data'),
            (12, 3, 'DAC addr')
        )
    ),
    6: (
        'DAC_WR',
        (
            (0, 12, 'DAC data'),
            (12, 3, 'DAC addr')
        )
    ),
    7: (
        'DAC_WR',
        (
            (0, 12, 'DAC data'),
            (12, 3, 'DAC addr')
        )
    ),
    'ADDR_IDX': (12, 3),
    'MSB_IDX': (15, 1),
}

#   0:  Field Configuration (Tuple)
#       0:  start bit    : int
#       1:  width        : int
#       2:  field name   : int
#       3:  field parser : function(field_value, decoder_options) -> str
MISO_READING = {
    'ADC_RESULT': (
        (0, 12, 'ADC data', raw_voltage),
        (12, 3, 'ADC_ADDR'),
    ),
    'TMP_SENSE_RESULT': (
        (0, 12, 'Temperature data', raw_temperature),
        (12, 4, 'TEMPSENSE_ADDR', empty_str),
    ),
    'DAC_DATA_RD': (
        (0, 12, 'DAC data', raw_voltage),
        (12, 3, 'DAC addr'),
    ),
    'REG_READ': (
        
    ),
}
