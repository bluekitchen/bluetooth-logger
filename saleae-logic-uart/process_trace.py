#!/usr/bin/env python
# BlueKitchen GmbH (c) 2018

# convert logic analyzer cvs trace log output to PacketLogger format
# can be viewed with Wireshark

# logic analyzer trace format:
#   HEADER
#   Timestamp (float), channel 0, channel 1, ..
#   ...

# APPLE PacketLogger
# typedef struct {
#   uint32_t    len;
#   uint32_t    ts_sec;
#   uint32_t    ts_usec;
#   uint8_t     type;   // 0xfc for note
# }

import re
import sys
import time
import os


# add our libs
sys.path.append(os.path.abspath(os.path.dirname(sys.argv[0]) + '/../lib'))

# import packet logger
import packetlogger

# HCI H4 Parser

def read_little_endian_16(buffer, offset):
    return buffer[offset] | buffer[offset+1] << 8

class hci_h4_parser:
    type = 0
    data = bytearray()
    timestamp = 0
    incoming = False
    detected = False

    def process_byte(self, timestamp, byte):
        if self.type == 0:
            if not byte in [1,2,4]:
                print ("%f: Invalid packet type %x, incoming %u" % (timestamp, byte, self.incoming))
                return
            self.type = byte
            self.timestamp = timestamp
            self.data = bytearray()

            # auto-detect RX and TX lines
            if not self.detected:
                # - packet type == HCI Event   => Controller TX - Host RX
                # - packet type == HCI Command => Controller RX - Host TX
                if self.type == 0x04:
                    self.detected = True
                    self.incoming = True
                if self.type == 0x01:
                    self.detected = True
                    self.incoming = False
            return

        self.data.append(byte)

    def packet_complete(self):
        if self.type == 1:
            if len(self.data) < 3:
                return False
            plen = 3 + self.data[2]
            return len(self.data) >= plen
        if self.type == 2:
            if len(self.data) < 4:
                return False
            plen = 4 + read_little_endian_16(self.data, 2)
            return len(self.data) >= plen
        if self.type == 4:
            if len(self.data) < 2:
                return False
            plen = 2 + self.data[1]
            return len(self.data) >= plen
        return False

    def reset(self):
        self.type = 0

# UART Analzyer

class uart_analyzer:

    # config
    name = ''
    bit_time = 0.0

    # analyzer state
    analyzer_state = 'wait_for_idle'
    analyzer_value = 0
    analyzer_pos   = 0

    # input processor
    wait_for_time = -1
    wait_for_value = -1
    last_timestamp = -1
    last_value = -1

    # msg
    def msg(self, time, msg):
        print("%.9f-%s: %s" % (time, self.name, msg))

    # analyzer states
    def state_wait_for_idle(self, time, value):
        # self.msg(time, 'state_wait_for_idle')
        if value == 1:
            # self.msg(time, 'Idle, wait for start bit')
            self.engine_wait_for_value(0, 'wait_for_start')

    def state_wait_for_start(self, time,value):
        # self.msg(time, 'state_wait_for_start, value %u' % value)
        if value == 0:
            time_first_sample = timestamp + 1.5 * self.bit_time
            self.analyzer_value = 0
            self.analyzer_pos = 0
            self.engine_wait_for_time(time_first_sample, 'wait_for_bit')
        else:
            self.msg(time, 'error: expected value = 0')

    def state_wait_for_bit(self, time, value):
        self.analyzer_value |=  (value << self.analyzer_pos)
        # self.msg(time, 'state_wait_for_bit, (pos %u) value %u => %02x' % (self.analyzer_pos, value, self.analyzer_value))
        self.analyzer_pos += 1
        next_time = time + self.bit_time
        if self.analyzer_pos == 8:
            next_state = 'wait_for_stop'
        else:
            next_state = 'wait_for_bit'
        self.engine_wait_for_time(time + self.bit_time, next_state)

    def state_wait_for_stop(self, time, value):
        if value == 0:
            self.msg(time, 'Stop: expected high value as stop bit')
        else:
            # self.msg(time, 'Byte complete %02x' % self.analyzer_value)
            self.hci_h4_parser.process_byte(time, self.analyzer_value)
        self.engine_wait_for_value(0, 'wait_for_start')

    def analyzer_step(self, time, value):
        if self.analyzer_state ==  'wait_for_idle':
            self.state_wait_for_idle(time, value)
        elif self.analyzer_state == 'wait_for_start':
            self.state_wait_for_start(time,value)
        elif self.analyzer_state == 'wait_for_bit':
            self.state_wait_for_bit(time,value)
        elif self.analyzer_state == 'wait_for_stop':
            self.state_wait_for_stop(time,value)
        else:
            print("Invalid state: %s" % self.analyzer_state)

    # engine
    def engine_wait_for_value(self, value, state):
        # print('wait for value %u called -> %s' % (value, state))
        self.wait_for_value = value
        self.analyzer_state = state

    def engine_wait_for_time(self, time, state):
        # print('wait for time %.9f called -> %s' % (time, state))
        self.wait_for_time = time
        self.analyzer_state = state

    def input_process(self, timestamp, value):
        # print('input: %.9f, value %u (wait_for_time %.9f, wait_for_value %d)' % (timestamp, value, self.wait_for_time, self.wait_for_value))
        done = False
        while not done:
            done = True
            if self.wait_for_time >= 0:
                if timestamp >= self.wait_for_time:
                    done = False
                    ts = self.wait_for_time
                    self.wait_for_time = -1
                    self.analyzer_step(ts, self.last_value)
            elif self.wait_for_value >= 0:
                if value == self.wait_for_value:
                    done = False
                    self.wait_for_value = -1
                    self.analyzer_step(timestamp, value)
            else:
                self.analyzer_step(timestamp, value)
        self.last_timestamp = timestamp
        self.last_value = value

    # constructor
    def __init__(self, name, baudrate, hci_h4_parser):
        self.name = name
        self.bit_time = 1.0 / baudrate
        self.hci_h4_parser = hci_h4_parser
        # self.msg(0, "Baud %u, bit time: %.9f s" % (baudrate, self.bit_time))

# Main

def byte_to_str(data):
    return ''.join( [ "%02X " % x for x in data ] ).strip()

if len(sys.argv) == 1:
    print('Logic Analyzer CSV to PacketLogger converter')
    print('Copyright 2018, BlueKitchen GmbH')
    print('')
    print('Usage: ', sys.argv[0], 'file.csv [hci_dump.pkgl]')
    print('Converted hci_dump.pklg can be viewed with Wireshark and OS X PacketLogger')
    exit(0)

infile = sys.argv[1]
outfile = os.path.splitext(infile)[0] + ".pklg"
if len(sys.argv) > 2:
    outfile = sys.argv[2]

# config
baudrate = 115200

# with open(outfile, 'w') as fout:
with open (outfile, 'wb') as fout:
    with open (infile, 'rt') as fin:
        # skip header
        line = fin.readline()
        fields = line.strip().split(',')
        channels = fields[1:]
        analyzers = [ uart_analyzer(name.strip(), baudrate, hci_h4_parser()) for name in channels if not 'RTS' in name];
        for line in fin:
            fields = line.strip().split(',')
            timestamp = float(fields[0])
            values = fields[1:]
            for (analyzer,value) in zip(analyzers,values):
                analyzer.input_process(timestamp, int(value))
                parser = analyzer.hci_h4_parser
                if parser.packet_complete():
                    packet_log_type = packetlogger.packet_log_type_for_hci_type_and_incoming(parser.type, parser.incoming)
                    if parser.type == 2:
                        print(parser.type, parser.incoming, packet_log_type, parser.timestamp, byte_to_str(parser.data))
                    packetlogger.dump_packet(fout, parser.timestamp, packet_log_type, parser.data)
                    parser.reset()



