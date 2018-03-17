#!/usr/bin/env python

import struct
import time
import sys
import os

# pcap(ng) parser
import pcapng
from pcapng.blocks import SectionHeader, InterfaceDescription, EnhancedPacket

# Import our PacketLogger lib
sys.path.append('../lib')
import packetlogger

def as_hex(data):
    str_list = []
    for byte in data:
        str_list.append("{0:02x} ".format(ord(byte)))
    return ''.join(str_list)

if len(sys.argv) == 1:
    print('Windows USBPcap to PacketLogger converter')
    print('Copyright 2018, BlueKitchen GmbH')
    print('')
    print('Usage: %s capture.pcapng' % sys.argv[0])
    print('Converted capture.pklg can be viewed with Wireshark and OS X PacketLogger')
    exit(0)

infile = sys.argv[1]
outfile = os.path.splitext(infile)[0] + ".pklg"
if len(sys.argv) > 2:
    outfile = sys.argv[2]

with open(infile) as fp:
    scanner = pcapng.FileScanner(fp)
    event_endpoint = -1

    # open hci_dump.pklg
    with open (outfile, 'wb') as fout:

        # microseconds
        timestamp_resolution = 0.000001

        for block in scanner:

            # TODO: parse if_tsresol in options
            # if isinstance(block, InterfaceDescription):
            #     print(block)

            if isinstance(block, EnhancedPacket):
                usb_data = block.packet_data
                
                function = struct.unpack_from("<H", usb_data, 14)[0]
                data_len = struct.unpack_from("<I", usb_data, 23)[0]
                endpoint = struct.unpack_from( "B", usb_data, 21)[0]

                if data_len == 0:
                    continue

                timestamp_high = block.timestamp_high
                timestamp_low  = block.timestamp_low

                tv_sec  = ((timestamp_high << 32) + timestamp_low) * timestamp_resolution
                tv_usec = (tv_sec - int(tv_sec)) * 1000000
                tv_ms   = (tv_sec - int(tv_sec)) * 1000

                timestr = time.strftime("%H:%M:%S", time.gmtime(tv_sec)) + ".%03u" % tv_ms

                # Assumption: At least one HCI Event is received before any HCI ACL packets
                if function == 9:
                    if event_endpoint < 0:
                        event_endpoint = endpoint

                # Control Transer => CMD
                if function == 8:
                    packet_type  = 0
                    packet_data = block.packet_data[28:]

                # Bulk or Interrupt => EVT or ACL
                elif function == 9:
                    packet_data = block.packet_data[27:]
                    if endpoint == event_endpoint:
                        packet_type = 1
                    elif endpoint > 0x80:
                        packet_type = 3
                    else:
                        packet_type = 2

                else:
                    continue

                packetlogger.dump_packet(fout, tv_sec, packet_type, packet_data)

        print("Packet Log: %s" % outfile)
