#!/usr/bin/env python
#==========================================================================
# (c) 2017  BlueKitchen GmbH
#--------------------------------------------------------------------------
# Capture Bluetooth HCI Traffic using Beagle USB Protocol Analyzer
#==========================================================================

#==========================================================================
# IMPORTS
#==========================================================================
from beagle_py import *
import datetime

# add our libs
sys.path.append(os.path.abspath(os.path.dirname(sys.argv[0]) + '/../lib'))

# import packet logger
import packetlogger

#==========================================================================
# GLOBALS
#==========================================================================
beagle = 0
samplerate_khz = 0;
IDLE_THRESHOLD = 2000

#==========================================================================
# UTILITY FUNCTIONS
#==========================================================================
def TIMESTAMP_TO_NS (stamp, samplerate_khz):
    return int((stamp * 1000) / (samplerate_khz/1000))

def print_general_status (status):
    """ General status codes """

    if (status == BG_READ_OK) :
        print "OK",

    if (status & BG_READ_TIMEOUT):
        print "TIMEOUT",

    if (status & BG_READ_ERR_MIDDLE_OF_PACKET):
        print "MIDDLE",

    if (status & BG_READ_ERR_SHORT_BUFFER):
        print "SHORT BUFFER",

    if (status & BG_READ_ERR_PARTIAL_LAST_BYTE):
        print "PARTIAL_BYTE(bit %d)" % (status & 0xff),

def print_usb_status (status):
    """USB status codes"""
    if (status & BG_READ_USB_ERR_BAD_SIGNALS):   print "BAD_SIGNAL;",
    if (status & BG_READ_USB_ERR_BAD_SYNC):      print "BAD_SYNC;",
    if (status & BG_READ_USB_ERR_BIT_STUFF):     print "BAD_STUFF;",
    if (status & BG_READ_USB_ERR_FALSE_EOP):     print "BAD_EOP;",
    if (status & BG_READ_USB_ERR_LONG_EOP):      print "LONG_EOP;",
    if (status & BG_READ_USB_ERR_BAD_PID):       print "BAD_PID;",
    if (status & BG_READ_USB_ERR_BAD_CRC):       print "BAD_CRC;",

def print_usb_events (events):
    """USB event codes"""
    if (events & BG_EVENT_USB_HOST_DISCONNECT):   print "HOST_DISCON;",
    if (events & BG_EVENT_USB_TARGET_DISCONNECT): print "TGT_DISCON;",
    if (events & BG_EVENT_USB_RESET):             print "RESET;",
    if (events & BG_EVENT_USB_HOST_CONNECT):      print "HOST_CONNECT;",
    if (events & BG_EVENT_USB_TARGET_CONNECT):    print "TGT_CONNECT/UNRST;",

def usb_print_summary (i, count_sop, summary):
    count_sop_ns =  TIMESTAMP_TO_NS(count_sop, samplerate_khz)
    print "%d,%u,USB,( ),%s" % (i, count_sop_ns, summary)


#==========================================================================
# USB DUMP FUNCTIONS
#==========================================================================
# Renders packet data for printing.
def usb_print_data_packet (packet, length):
    packetstring = ""

    if (length == 0):
        return packetstring

    # Get the packet identifier
    pid = packet[0]

    # Print the packet identifier
    if    (pid ==  BG_USB_PID_OUT):      pidstr = "OUT"
    elif  (pid ==  BG_USB_PID_IN):       pidstr = "IN"
    elif  (pid ==  BG_USB_PID_SOF):      pidstr = "SOF"
    elif  (pid ==  BG_USB_PID_SETUP):    pidstr = "SETUP"
    elif  (pid ==  BG_USB_PID_DATA0):    pidstr = "DATA0"
    elif  (pid ==  BG_USB_PID_DATA1):    pidstr = "DATA1"
    elif  (pid ==  BG_USB_PID_DATA2):    pidstr = "DATA2"
    elif  (pid ==  BG_USB_PID_MDATA):    pidstr = "MDATA"
    elif  (pid ==  BG_USB_PID_ACK):      pidstr = "ACK"
    elif  (pid ==  BG_USB_PID_NAK):      pidstr = "NAK"
    elif  (pid ==  BG_USB_PID_STALL):    pidstr = "STALL"
    elif  (pid ==  BG_USB_PID_NYET):     pidstr = "NYET"
    elif  (pid ==  BG_USB_PID_PRE):      pidstr = "PRE"
    elif  (pid ==  BG_USB_PID_SPLIT):    pidstr = "SPLIT"
    elif  (pid ==  BG_USB_PID_PING):     pidstr = "PING"
    elif  (pid ==  BG_USB_PID_EXT):      pidstr = "EXT"
    else: pidstr = "INVALID"

    packetstring += pidstr + ","

    # Print the packet data
    for n in range(length):
        packetstring += "%02x " % packet[n]

    return packetstring

# Track Bluetooth HCI Packets
state_idle        = 0
state_in_w4_event = 1
state_in_w4_acl   = 2
state_out_w4_cmd  = 3
state_out_w4_acl  = 4
bluetooth_state   = state_idle

# hci packet
cmd_out_buffer  = array_u08(0)
event_in_buffer = array_u08(0)
acl_in_buffer   = array_u08(0)
acl_out_buffer  = array_u08(0)
hci_packet_sop  = 0;

# Identify endpoints
control_endpoint =   -1;
interrupt_endpoint = -1;

hci_dump_fout = -1

def hex_for_packet(packet):
    result = ""
    for n in range(len(packet)):
        result += "%02x " % packet[n]
    return result

def bluetooth_dump_packet(type, packet):
    global hci_packet_sop
    global hci_dump_fout

    # output in BTstack's text format
    # time_obj = datetime.datetime( 2000, 1, 1 ) + datetime.timedelta( 0, 0, 0, hci_packet_sop / 1000000 )
    # time = time_obj.time().strftime("%H:%M:%S:%f")[:-3]
    # print('[%s] %s %s' % (time, type, hex_for_packet(packet)))

    # output in PacketLogger format
    timestamp = hci_packet_sop / 1000000000.0
    packetlogger.dump_packet(hci_dump_fout, timestamp, type, packet)

def bluetooth_process_cmd_out(data, length):
    global cmd_out_buffer
    cmd_out_buffer = cmd_out_buffer + data
    command_length = 3 + cmd_out_buffer[2]
    if command_length <= len(cmd_out_buffer):
        bluetooth_dump_packet(0, cmd_out_buffer)
        cmd_out_buffer   = array_u08(0)

def bluetooth_process_event_in(data, length):
    global event_in_buffer
    event_in_buffer = event_in_buffer + data
    if len(event_in_buffer) < 2:
        return
    acl_length = 2 + event_in_buffer[1]
    if acl_length <= len(event_in_buffer):
        bluetooth_dump_packet(1, event_in_buffer)
        event_in_buffer = array_u08(0)

def bluetooth_process_acl_out(data, length):
    global acl_out_buffer
    acl_out_buffer = acl_out_buffer + data
    if len(acl_in_buffer) < 4:
        return
    acl_length = 4 + acl_out_buffer[2] + acl_out_buffer[3] * 256
    if acl_length <= len(acl_out_buffer):
        bluetooth_dump_packet(2, acl_out_buffer)
        acl_out_buffer   = array_u08(0)

def bluetooth_process_acl_in(data, length):
    global acl_in_buffer
    acl_in_buffer = acl_in_buffer + data
    if len(acl_in_buffer) < 4:
        return
    acl_length = 4 + acl_in_buffer[1]
    if acl_length <= len(acl_in_buffer):
        bluetooth_dump_packet(3, acl_out_buffer)
        acl_in_buffer = array_u08(0)

def bluetooth_process_usb_packet(time_sop, packet, length):
    global bluetooth_state
    global state_idle
    global state_in_w4_event
    global state_out_w4_cmd
    global state_in_w4_acl
    global state_out_w4_acl
    global control_endpoint
    global hci_packet_sop
    global interrupt_endpoint

    data_pids = [ BG_USB_PID_DATA0, BG_USB_PID_DATA1]
    done_pids = [ BG_USB_PID_ACK, BG_USB_PID_NAK, BG_USB_PID_STALL]

    # print (usb_print_data_packet(packet, length))

    if (length == 0):
        return

    # Get the packet identifier
    pid = packet[0]

    # Find Control Endpoint
    if control_endpoint == -1 and pid == BG_USB_PID_SETUP:
        control_endpoint = packet[2]

    # Assumption: At least one HCI Event is received before any HCI ACL packets
    if interrupt_endpoint == -1 and control_endpoint != -1 and pid == BG_USB_PID_IN and packet[2] != control_endpoint:
        interrupt_endpoint = packet[2]

    if bluetooth_state == state_idle:
        if pid == BG_USB_PID_OUT:
            if packet[2] == control_endpoint:
                bluetooth_state = state_out_w4_cmd
            else:
                bluetooth_state = state_out_w4_acl
            hci_packet_sop = time_sop
        elif pid == BG_USB_PID_IN:
            if packet[2] == interrupt_endpoint:
                bluetooth_state = state_in_w4_event
            else:
                bluetooth_state = state_in_w4_acl
            hci_packet_sop = time_sop
    elif bluetooth_state == state_out_w4_cmd:
        if pid in data_pids:
            data = packet[1:length-2]
            bluetooth_process_cmd_out(data, length-3)
        elif pid in done_pids:
            bluetooth_state = state_idle
    elif bluetooth_state == state_out_w4_acl:
        if pid in data_pids:
            data = packet[1:length-2]
            bluetooth_process_acl_out(data, length-3)
        elif pid in done_pids:
            bluetooth_state = state_idle
    elif bluetooth_state == state_in_w4_event:
        if pid in data_pids:
            data = packet[1:length-2]
            bluetooth_process_event_in(data, length-3)
        elif pid in done_pids:
            bluetooth_state = state_idle
    elif bluetooth_state == state_in_w4_acl:
        if pid in data_pids:
            data = packet[1:length-2]
            bluetooth_process_acl_in(data, length-3)
        elif pid in done_pids:
            bluetooth_state = state_idle

# Print common packet header information
def usb_print_packet (packet_number, time_sop, status, events, error_status,
                      packet_data):
    if (error_status == 0):  error_status = ""

    sys.stdout.write("%d,%u,USB,(%s " % (packet_number, time_sop,
                                         error_status))
    print_general_status(status)
    print_usb_status(status)
    print_usb_events(events)

    if (packet_data == 0):  packet_data = ""
    print "),%s" % packet_data
    sys.stdout.flush()

# Dump saved summary information
def usb_print_summary_packet (packet_number, count_sop, sof_count, pre_count,
                              in_ack_count, in_nak_count, sync_errors):
    offset = 0
    summary = ""
    if (sof_count or in_ack_count or in_nak_count or pre_count):
        summary +=  "COLLAPSED "

        if (sof_count > 0):
            summary += "[%d SOF] " %  sof_count

        if (pre_count > 0):
            summary += "[%d PRE/ERR] " % pre_count

        if (in_ack_count > 0):
            summary += "[%d IN/ACK] " % in_ack_count

        if (in_nak_count > 0):
            summary += "[%d IN/NAK] " % in_nak_count

        # usb_print_summary(packet_number+offset, count_sop, summary)
        offset += 1

    # Output any sync errors
    if (sync_errors > 0):
        summary += "<%d SYNC ERRORS>" %  sync_errors
        usb_print_summary(packet_number+offset, count_sop, summary)
        offset += 1
    return offset

# If the packet is not one that we're aggregating,
# this function returns 1, else 0.
def usb_trigger (pid):
    return ((pid != BG_USB_PID_SOF)  and
            (pid != BG_USB_PID_PRE)  and
            (pid != BG_USB_PID_IN)   and
            (pid != BG_USB_PID_ACK)  and
            (pid != BG_USB_PID_NAK))

# The main packet dump routine
def usbdump():
    timing_size = bg_bit_timing_size(BG_PROTOCOL_USB, 1024)

    count_sop    = 0
    sof_count    = 0
    pre_count    = 0
    in_ack_count = 0
    in_nak_count = 0

    pid        = 0
    last_sop   = 0
    last_pid   = 0

    sync_errors = 0

    packetnum = 0

    saved_in_length = 0
    saved_in_status = 0

    global samplerate_khz;
    samplerate_khz = bg_samplerate(beagle, 0)
    idle_samples   = IDLE_THRESHOLD * samplerate_khz

    # Open the connection to the Beagle.  Default to port 0.
    if (bg_enable(beagle, BG_PROTOCOL_USB) != BG_OK):
        print "error: could not enable USB capture; exiting..."
        sys.exit(1)

    # Allocate the arrays to be passed into the read function
    packet = array_u08(1024)
    timing = array_u32(timing_size)

    # ...then start decoding packets
    while True:
        last_pid = pid
        (length, status, events, time_sop, time_duration,
         time_dataoffset, packet, timing) = \
            bg_usb2_read_bit_timing (beagle, packet, timing)


        time_sop_ns = TIMESTAMP_TO_NS(time_sop, samplerate_khz)

        # Check for invalid packet or Beagle error
        if (length < 0):
            error_status = "error=%d" % length
            usb_print_packet(packetnum, time_sop_ns, status, events,
                             error_status, 0)
            break

        # Check for USB error
        if (status == BG_READ_USB_ERR_BAD_SYNC):
            sync_errors += 1

        if (length > 0):
            pid = packet[0]
        else:
            pid = 0

        # Check the PID and collapse appropriately:
        # SOF* PRE* (IN (ACK|NAK))*
        # If we have saved summary information, and we have
        # hit an error, received a non-summary packet, or
        # have exceeded the idle time, then dump out the
        # summary information before continuing
        if (status != BG_READ_OK or usb_trigger(pid) or
            (int(time_sop - count_sop) >= idle_samples)):
            offset = usb_print_summary_packet(packetnum, count_sop, sof_count, pre_count, in_ack_count, in_nak_count, sync_errors)
            sof_count    = 0
            pre_count    = 0
            in_ack_count = 0
            in_nak_count = 0
            sync_errors  = 0
            count_sop    = time_sop

            # Adjust the packet index if any events were printed by
            # usb_print_summary_packet.
            packetnum += offset

        # Now handle the current packet based on its packet ID
        if (pid == BG_USB_PID_SOF):
            # Increment the SOF counter
            sof_count += 1

        elif (pid ==  BG_USB_PID_PRE):
            # Increment the PRE counter
            pre_count += 1

        elif (pid == BG_USB_PID_IN):
            # If the transaction is an IN, don't display it yet and
            # save the transaction.
            # If the following transaction is an ACK or NAK,
            # increment the appropriate IN/ACK or IN/NAK counter.
            # If the next transaction is not an ACK or NAK,
            # display the saved IN transaction .
            saved_in            = packet[:length]
            saved_in_timing     = timing[:length*8]
            saved_in_sop        = time_sop
            saved_in_duration   = time_duration
            saved_in_dataoffset = time_dataoffset
            saved_in_length     = length
            saved_in_status     = status
            saved_in_events     = events

        else:
            if ((pid ==  BG_USB_PID_NAK or pid == BG_USB_PID_ACK) and
                # If the last transaction was IN, increment the appropriate
                # counter and don't display the transaction.
                saved_in_length > 0):
                saved_in_length = 0
                if (pid == BG_USB_PID_ACK):
                    in_ack_count += 1
                else:
                    in_nak_count += 1
            else:
                #If the last transaction was IN, output it
                if (saved_in_length > 0):
                    saved_in_sop_ns = TIMESTAMP_TO_NS(saved_in_sop, samplerate_khz)
                    bluetooth_process_usb_packet(saved_in_sop_ns, saved_in, saved_in_length)
                    packetnum += 1
                    saved_in_length = 0


                # Output the current transaction
                if (length > 0 or events != 0  or
                    (status != 0 and status != BG_READ_TIMEOUT)):
                    bluetooth_process_usb_packet(time_sop_ns, packet, length)
                    packetnum += 1

                last_sop  = time_sop
                count_sop = time_sop + time_duration

    # Stop the capture
    bg_disable(beagle)

#==========================================================================
# MAIN PROGRAM ENTRY POINT
#==========================================================================
port       = 0      # open port 0 by default
samplerate = 0      # in kHz (query)
timeout    = 500    # in milliseconds
latency    = 200    # in milliseconds
num        = 0

# Open the device
beagle = bg_open(port)
if (beagle <= 0):
    print "Unable to open Beagle device on port %d" % port
    print "Error code = %d" % beagle
    sys.exit(1)

print "Opened Beagle device on port %d" % port

# Query the samplerate since Beagle USB has a fixed sampling rate
samplerate = bg_samplerate(beagle, samplerate)
if (samplerate < 0):
    print "error: %s" % bg_status_string(samplerate)
    sys.exit(1)

print "Sampling rate set to %d KHz." % samplerate

# Set the idle timeout.
# The Beagle read functions will return in the specified time
# if there is no data available on the bus.
bg_timeout(beagle, timeout)
print "Idle timeout set to %d ms." %  timeout

# Set the latency.
# The latency parameter allows the programmer to balance the
# tradeoff between host side buffering and the latency to
# receive a packet when calling one of the Beagle read
# functions.
bg_latency(beagle, latency)
print "Latency set to %d ms." % latency

bg_host_ifce_speed_string = ""

if (bg_host_ifce_speed(beagle)):
    bg_host_ifce_speed_string = "high speed"
else:
    bg_host_ifce_speed_string = "full speed"

print "Host interface is %s." % bg_host_ifce_speed_string

# There is usually no need for pullups or target power
# when using the Beagle as a passive monitor.
bg_target_power(beagle, BG_TARGET_POWER_OFF)

print ""
sys.stdout.flush()

# open hci_dump.pklg
with open ('hci_dump.pklg', 'wb') as fout:
    hci_dump_fout = fout
    usbdump()

# Close the device
bg_close(beagle)

sys.exit(0)
