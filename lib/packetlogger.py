#!/usr/bin/env python
# BlueKitchen GmbH (c) 2018

# Store HCI packets in PacketLogger format
# can also be viewed with Wireshark

# packet logger types
# - 0x00 HCI Command
# - 0x01 HCI Event
# - 0x02 HCI ACL Out
# - 0x03 HCI ACL In

# APPLE PacketLogger
# typedef struct {
#   uint32_t    len;
#   uint32_t    ts_sec;
#   uint32_t    ts_usec;
#   uint8_t     type;   // 0xfc for note
# }

def array_for_big_endian_32(value):
    return bytearray([value >> 24, (value >> 16) & 0xff, (value >> 8) & 0xff, value & 0xff])

def dump_packet(fout, timestamp, type, data):
    length = 9 + len(data)
    tv_sec  =  int(timestamp)
    tv_usec = int((timestamp - tv_sec) * 1000000)
    fout.write(array_for_big_endian_32(length))
    fout.write(array_for_big_endian_32(tv_sec))
    fout.write(array_for_big_endian_32(tv_usec))
    fout.write(bytearray([type]))
    fout.write(data)

def packet_log_type_for_hci_type_and_incoming(hci_type, incoming):
    packet_log_type = -1
    if hci_type == 1:
        packet_log_type = 0
    elif hci_type == 2:
        if incoming:
            packet_log_type = 3
        else:
            packet_log_type = 2
    elif hci_type == 4:
        packet_log_type = 1
    else:
        print('packet type %x' % hci_type)
    return packet_log_type
