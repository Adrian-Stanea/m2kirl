##
# This file is part of the libsigrokdecode project.
##
# Copyright (C) 2020 Analog Devices Inc.
##
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
##
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
##
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
##
import sigrokdecode as srd
from common.srdhelper import bitpack_lsb, bitpack_msb, SrdIntEnum
from .lists import *

import logging
from datetime import datetime
import os


(NAME_IDX, DESC_IDX) = range(2)
Ann = SrdIntEnum.from_str('Ann', 'MOSI_REG MOSI_FIELD MISO_REG MISO_FIELD')
St = SrdIntEnum.from_str('St', 'INVALID READBACK ADC_OP')


class Decoder(srd.Decoder):
    api_version = 3
    id = 'ad5592r'
    name = 'AD5592R'
    longname = 'Analog Devices AD5592R'
    desc = 'Analog Devices AD5592R 12-bit configurable ADC/DAC.'
    license = 'gplv2+'
    inputs = ['spi']
    outputs = []
    tags = ['IC', 'Analog/digital']
    
    options = (
        {'id': 'v_ref', 'desc': 'Reference Voltage [V]', 'default': 2.5},
    )

    annotations = (
        ('mosi-register', 'MOSI Register'),
        ('mosi-field', 'MOSI Field'),
        ('miso-register', 'MISO Register'),
        ('miso-field', 'MISO Field'),
    )
    annotation_rows = (
        ('mosi-registers', 'MOSI Registers',        (Ann.MOSI_REG,)),
        ('mosi-fields',    'MOSI Fields',           (Ann.MOSI_FIELD,)),
        ('miso-registers', 'MISO Registers',        (Ann.MISO_REG,)),
        ('miso-fields',    'MISO Fields',           (Ann.MISO_FIELD,)),
    )

    def init_logger(self):
        logging.basicConfig(filemode='w',
                            format='%(levelname)s - %(message)s',
                            # handlers=[logging.StreamHandler(sys.stdout)]  # Output to stdout
                            )
        self.logger = logging.getLogger()
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(logging.DEBUG)

    def log_machine_state(self):
        self.logger.debug("MACHINE STATE VARIABLES")

        self.logger.debug("\tself.state = %s", self.state)
        self.logger.debug("\tself.crnt_mosi_reg_name = %s",
                          self.crnt_mosi_reg_name)
        self.logger.debug("\tself.miso_format = %s", self.miso_fields_format)
        self.logger.debug("\tself.miso_crnt_read = %d", self.miso_crnt_read)
        self.logger.debug("\tself.miso_delay = %d", self.miso_delay)
        self.logger.debug("\tself.miso_adc_op_len = %d", self.miso_adc_op_len)
        self.logger.debug("\tself.miso_adc_op_repeat = %d",
                          self.miso_adc_op_repeat)

    def log_bits(self, bits, name):
        self.logger.debug("LOGGING BITS")
        self.logger.debug("\tname = %s", name)
        self.logger.debug("\tlen(bits) = %d", len(bits))
        for idx, bit in enumerate(bits):
            self.logger.debug(
                "\t\tbits[%d] = %d \t ss = %d \t es = %d", idx, bit[0], bit[1], bit[2])
        self.logger.debug("\t\tbits value = %xh", bitpack_msb(bits, 0))

    def __init__(self,):
        self.init_logger()

        self.MOSI_REG_READ_CMD_LIST = [
            'DAC_RD', 'CONFIG_READ_AND_LDAC', 'ADC_SEQ', 'ADC_CONFIG']
        self.reset()

    def start(self):
        self.out_ann = self.register(srd.OUTPUT_ANN)

    def reset(self):
        self.reset_data()
        self.reset_state()

    def reset_data(self):
        '''
            Track of current chunck of data to be decoded
        '''
        self.logger.debug("reset_data call")
        self.ss_cmd = -1
        self.es_cmd = -1
        self.nb_bits_in_frame = 0
        self.mosi = []
        self.miso = []

    def reset_state(self):
        ''' 
            Current state of the decoder determines how we annotate MISO readings.
            MOSI always decode in the same way
        '''
        self.state = St.INVALID
        self.crnt_mosi_reg_name = None

        # ADC data readings depend on the command that was sent
        self.miso_fields_format = None
        self.miso_temp_read = 0
        self.miso_adc_op_repeat = False
        self.miso_adc_op_len = 0        # number of ADC_OP reads
        # MISO wont read ADC_OP after first cycle -> delay 1 NOOP
        self.miso_delay = 0
        self.miso_crnt_read = 0

    def putg(self, ss, es, ann_idx, data):
        ''' Put an annotation on the output graphic channel: sigrok-cli or pulseview.'''
        self.put(ss, es, self.out_ann, [ann_idx, data, ])

    def decode_word(self):
        """
            - Interpret a 16bit word when accumulation of bits is complete
        """
        # Holding bits in LSB order during interpretation simplifies
        # bit field extraction. And annotation emitting routines expect
        # this reverse order of bits' timestamps.
        self.logger.debug("decode_word call")
        self.logger.debug("STATE = %s", self.state)

        self.log_bits(self.mosi, "BEFORE REVERSE self.mosi")
        self.mosi.reverse()
        self.handle_mosi()

        self.log_bits(self.miso, "BEFORE REVERSE self.miso")
        self.miso.reverse()
        self.handle_miso()

    def store_bits(self, mosi_bits, miso_bits):
        '''Store the bits in the order they are seen in the SPI frames in MSB order.'''
        cp_mosi_bits = mosi_bits.copy()
        cp_mosi_bits.reverse()
        self.mosi.extend(cp_mosi_bits)

        cp_miso_bits = miso_bits.copy()
        cp_miso_bits.reverse()
        self.miso.extend(cp_miso_bits)

        self.nb_bits_in_frame += len(cp_mosi_bits)

        self.log_bits(cp_mosi_bits, "cp_mosi_bits")
        self.log_bits(cp_miso_bits, "cp_miso_bits")
        self.logger.debug("\t self.nb_bits = %d", self.nb_bits_in_frame)

    def handle_mosi(self):
        self.logger.debug("handle_mosi call")

        offset, width = CTRL_REGISTERS.get('MSB_IDX')
        MSB, (_, _, ) = self.decode_bits(self.mosi, offset, width)

        self.logger.debug("\t MSB = %d", MSB)

        if MSB == 0:  # write to the control-register
            offset, width = CTRL_REGISTERS.get('ADDR_IDX')
            addr, (_, _, ) = self.decode_bits(self.mosi, offset, width)
            name = CTRL_REGISTERS.get(addr)[NAME_IDX]

            self.logger.debug(
                "\t name = %s \t ss_cmd=%s \t es_cmd = %s", name, self.ss_cmd, self.es_cmd)

            self.crnt_mosi_reg_name = name
            text = ['{name}'.format(name=name),]
            self.putg(self.ss_cmd, self.es_cmd, Ann.MOSI_REG, text)
            field_descs = CTRL_REGISTERS.get(addr, None)[DESC_IDX]
        elif MSB == 1:  # write to a DAC channel
            offset, width = DAC_CHANNELS.get('ADDR_IDX')
            addr, (_, _, ) = self.decode_bits(self.mosi, offset, width)
            text = ['DAC{addr} Write'.format(addr=addr),]
            self.putg(self.ss_cmd, self.es_cmd, Ann.MOSI_REG, text)
            field_descs = DAC_CHANNELS.get(addr, None)[DESC_IDX]
        # Interpret the register's content (when parsers are available) -> anotate mosi-field
        self.annotate_fields(self.mosi, Ann.MOSI_FIELD, field_descs)

    def handle_miso(self):
        self.logger.debug("handle_miso call")
        if self.state == St.INVALID:
            text = ['Invalid data']
            self.putg(self.ss_cmd, self.es_cmd, Ann.MISO_REG, text)
            return

        if self.state == St.READBACK:
            text = [self.miso_fields_format]
            self.putg(self.ss_cmd, self.es_cmd, Ann.MISO_REG, text)
            field_descs = MISO_READING[self.miso_fields_format]

        if self.state == St.ADC_OP:
            if self.miso_delay == 1:  # first reading is invalid -> delay 1 NOOP
                text = ['Invalid data']
                self.putg(self.ss_cmd, self.es_cmd, Ann.MISO_REG, text)
                self.miso_delay = 0
                return
            # rest of readings are valid
            if (self.miso_crnt_read % self.miso_adc_op_len) == 0 and self.miso_temp_read == 1:
                self.miso_fields_format = 'TMP_SENSE_RESULT'
            else:
                self.miso_fields_format = 'ADC_RESULT'

            text = [self.miso_fields_format]
            self.putg(self.ss_cmd, self.es_cmd, Ann.MISO_REG, text)
            field_descs = MISO_READING[self.miso_fields_format]

        self.annotate_fields(self.miso, Ann.MISO_FIELD, field_descs)
        self.miso_crnt_read = self.miso_crnt_read + 1

    def decode_bits(self, bits, offset, width):
        '''
            Extract content of a bit field segment.
            Expects LSB input data.
        '''
        bits = bits[offset:][:width]  # take a slice of the bits
        ss, es = bits[-1][1], bits[0][2]
        value = bitpack_lsb(bits, 0)
        return (value, (ss, es, ))

    def decode_field(self, bits, ann, name, offset, width, parser=None):
        '''Interpret a bit field. Emits an annotation.'''
        # Get the register field's content and position.
        val, (ss, es, ) = self.decode_bits(bits, offset, width)
        # Have the field's content formatted, emit an annotation.
        formatted = parser(val, self.options) if parser else '{}'.format(val)
        if formatted is not None and formatted != "":
            text = ['{name}: {val}'.format(name=name, val=formatted)]
        else:
            text = ['{name}'.format(name=name)]
        if text:
            self.putg(ss, es, ann, text)

    def annotate_fields(self, bits, ann, field_descs):
        if not field_descs:
            return
        for field_desc in field_descs:
            parser = None
            if len(field_desc) == 3:
                offset, width, name, = field_desc
            elif len(field_desc) == 4:
                offset, width, name, parser = field_desc
            elif len(field_desc) == 5:
                offset, width, name, parser, checker = field_desc
            else:
                raise Exception('Invalid field description')
            self.decode_field(bits, ann, name, offset,
                              width, parser)

    def handle_state(self):
        self.logger.debug("handle_state call")
        self.log_machine_state()

        if self.state == St.INVALID:
            self.state = self._next_ST_INVALID()
        elif self.state == St.READBACK:
            self.state = self._next_ST_READBACK()
        elif self.state == St.ADC_OP:
            self.state = self._next_ST_ADC_OP()
        else:
            raise (Exception("Invalid state"))

        self.logger.debug("NEXT STATE = %s", self.state)
        self.log_machine_state()

    def parse_mosi_state_cmd(self):
        self.logger.debug("parse_mosi_state_cmd call")
        self.logger.debug("MOSI register name = %s", self.crnt_mosi_reg_name)

        if self.crnt_mosi_reg_name in ['DAC_RD']:
            self.miso_fields_format = 'DAC_DATA_RD'
            return St.READBACK
        
        if self.crnt_mosi_reg_name in ['CONFIG_READ_AND_LDAC',]:
            REG_RD_EN = self.decode_bits(self.mosi, 6, 1)
            if REG_RD_EN:
                return St.READBACK
            return self.state

        if self.crnt_mosi_reg_name in ['ADC_SEQ']:
            REP_BIT, (_, _) = self.decode_bits(self.mosi, 9, 1)
            TEMP_BIT, (_, _) = self.decode_bits(self.mosi, 8, 1)
            NUM_CHANNELS, (_, _) = self.decode_bits(self.mosi, 0, 8)
            NUM_CHANNELS = bin(NUM_CHANNELS).count('1')

            if REP_BIT + TEMP_BIT + NUM_CHANNELS == 0:
                # command to reset ADC readings
                return St.INVALID

            self.miso_temp_read = TEMP_BIT
            self.miso_delay = 1  # next MISO will be invalid -> delay 1 NOOP
            self.miso_adc_op_len = TEMP_BIT + NUM_CHANNELS  # number of ADC_OP reads
            self.miso_adc_op_rep = bool(REP_BIT)
            self.miso_crnt_read = 0

            return St.ADC_OP

        if self.crnt_mosi_reg_name in ['ADC_CONFIG']:
            NUM_CHANNELS, (_, _) = self.decode_bits(self.mosi, 0, 8)
            NUM_CHANNELS = bin(NUM_CHANNELS).count('1')

            if NUM_CHANNELS == 0:
                # command to reset ADC readings
                return St.INVALID

            self.miso_delay = 1  # next MISO will be invalid -> delay 1 NOOP
            self.miso_adc_op_len = NUM_CHANNELS  # number of ADC_OP reads
            self.miso_crnt_read = 0

            return St.ADC_OP
        return self.state

    def _next_ST_INVALID(self):
        self.logger.debug("_next_ST_INVALID call")

        if self.crnt_mosi_reg_name in self.MOSI_REG_READ_CMD_LIST:
            return self.parse_mosi_state_cmd()
        return St.INVALID

    def _next_ST_READBACK(self):
        self.logger.debug("_next_ST_READBACK call")

        if self.crnt_mosi_reg_name in self.MOSI_REG_READ_CMD_LIST:
            return self.parse_mosi_state_cmd()
        return St.INVALID  # return to invalid state after readback

    def _next_ST_ADC_OP(self):
        self.logger.debug("_next_ST_ADC_OP call")

        if self.crnt_mosi_reg_name in self.MOSI_REG_READ_CMD_LIST:
            return self.parse_mosi_state_cmd()

        if self.miso_adc_op_repeat == False and self.miso_crnt_read == self.miso_adc_op_len:
            return St.INVALID  # return to invalid state after ADC sequence read

        return St.ADC_OP

    def cs_rising_edge(self, cs_old, cs_new):
        return cs_old is not None and cs_old == 0 and cs_new == 1

    def cs_falling_edge(self, cs_old, cs_new):
        return cs_old is not None and cs_old == 1 and cs_new == 0

    def decode(self, ss, es, data):
        ptype, _, _ = data
        self.logger.debug("ptype = %s \t ss = %d \t es = %d", ptype, ss, es)

        # NOTE: CS is active-low
        if ptype == 'CS-CHANGE':
            cs_old, cs_new = data[1:]
            self.logger.debug("\t cs_old = %d \t cs_new = %d", cs_old if cs_old else 0,
                              cs_new if cs_new else 0)

            # # start of a new 16 bit transaction
            if self.cs_falling_edge(cs_old, cs_new):
                self.logger.debug("\tFalling edge")

                self.reset_data()
                # self.ss_cmd = ss

            if self.cs_rising_edge(cs_old, cs_new):
                self.logger.debug("\tRising edge")

                # Invalid format after transaction
                if self.nb_bits_in_frame != 16:
                    self.reset_data()
                    return

                self.ss_cmd = self.mosi[0][1]
                self.es_cmd = self.mosi[-1][2]  # end of the word
                
                self.decode_word()
                self.handle_state()
                self.reset_data()
        if ptype == 'BITS':
            _, mosi_bits, miso_bits = data
            self.store_bits(mosi_bits, miso_bits)
