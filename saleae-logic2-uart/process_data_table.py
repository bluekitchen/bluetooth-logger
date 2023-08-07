#!/usr/bin/env python3
# BlueKitchen GmbH (c) 2023

# convert logic analyzer uart export to PacketLogger format
# can be viewed with Wireshark

# logic2 export format:
#   HEADER
#   Channel, Type, Timestamp (float), Duration, Data
#   ...

# APPLE PacketLogger
# typedef struct {
#   uint32_t    len;
#   uint32_t    ts_sec;
#   uint32_t    ts_usec;
#   uint8_t     type;   // 0xfc for note
# }

import sys
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
            if byte in [0x30, 0x31, 0x32, 0x33]:
                # Skip any eHCI low power packets
                return
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


# Main

def byte_to_str(data):
    return ''.join( [ "%02X " % x for x in data ] ).strip()

if len(sys.argv) <= 1:
    print('Logic2 Analyzer CSV to PacketLogger converter')
    print('Copyright 2023, BlueKitchen GmbH')
    print('')
    print('Usage: ', sys.argv[0], 'file.csv [hci_dump.pkgl]')
    print('Converted hci_dump.pklg can be viewed with Wireshark and OS X PacketLogger')
    exit(0)

infile = sys.argv[1]
outfile = os.path.splitext(infile)[0] + ".pklg"
if len(sys.argv) > 2:
    outfile = sys.argv[2]

# with open(outfile, 'w') as fout:
with open (outfile, 'wb') as fout:
    with open (infile, 'rt') as fin:
        # skip header
        line = fin.readline()        
        parser_dict = {}
        for line in fin:
            fields = line.strip().split(',')
            channel = fields[0]
            if channel not in parser_dict:
                parser_dict[channel] = hci_h4_parser()
            parser: hci_h4_parser = parser_dict[channel]
            timestamp = float(fields[2])
            value = int(fields[4], 16)
            parser.process_byte(timestamp, value)
            if parser.packet_complete():
                packet_log_type = packetlogger.packet_log_type_for_hci_type_and_incoming(parser.type, parser.incoming)
                if parser.type == 2:
                    print(parser.type, parser.incoming, packet_log_type, parser.timestamp, byte_to_str(parser.data))
                packetlogger.dump_packet(fout, parser.timestamp, packet_log_type, parser.data)
                parser.reset()



