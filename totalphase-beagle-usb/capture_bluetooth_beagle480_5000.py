#!/usr/bin/env python
#==========================================================================
# (c) 2007  Total Phase, Inc.
#--------------------------------------------------------------------------
# Project : Beagle Sample Code
# File    : capture_usb480.py
#--------------------------------------------------------------------------
# Simple Capture Example for Beagle USB 480
#--------------------------------------------------------------------------
# Redistribution and use of this file in source and binary forms, with
# or without modification, are permitted.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#==========================================================================

#==========================================================================
# IMPORTS
#==========================================================================
from beagle_py import *

# add our libs
sys.path.append(os.path.abspath(os.path.dirname(sys.argv[0]) + '/../lib'))

# import packet logger
import packetlogger

#==========================================================================
# GLOBALS
#==========================================================================
beagle         = 0
samplerate_khz = 0;
IDLE_THRESHOLD = 2000

# Packet groups
SOF              = 0
IN_ACK           = 1
IN_NAK           = 2
PING_NAK         = 3
SPLIT_IN_ACK     = 4
SPLIT_IN_NYET    = 5
SPLIT_IN_NAK     = 6
SPLIT_OUT_NYET   = 7
SPLIT_SETUP_NYET = 8
KEEP_ALIVE       = 9

# States used in collapsing state machine
IDLE        = 0
IN          = 1
PING        = 3
SPLIT       = 4
SPLIT_IN    = 5
SPLIT_OUT   = 7
SPLIT_SETUP = 8

# Size of packet queue.  At most this many packets will need to be alive
# at the same time.
QUEUE_SIZE = 3

# Disable COMBINE_SPLITS by setting to False.  Disabling
# will show individual split counts for each group (such as
# SPLIT/IN/ACK, SPLIT/IN/NYET, ...).  Enabling will show all the
# collapsed split counts combined.
COMBINE_SPLITS = True


#==========================================================================
# CLASSES
#==========================================================================
class PacketInfo:
    def __init__ (self):
        self.data            = array_u08(1024)
        self.time_sop        = 0
        self.time_sop_ns     = 0
        self.time_duration   = 0
        self.time_dataoffset = 0
        self.status          = 0
        self.events          = 0
        self.length          = 0

# Used to store the packets that are saved during the collapsing
# process.  The tail of the queue is always used to store
# the current packet.
class PacketQueue:
    def __init__ (self):
        self._tail = 0
        self._head = 0
        self.pkt   = [ PacketInfo() for i in xrange(QUEUE_SIZE) ]

    def __getattr__ (self, attr):
        if attr == 'tail':
            return self.pkt[self._tail]
        if attr == 'head':
            return self.pkt[self._head]
        raise AttributeError("%s not an attribute of PacketQueue" % attr)

    def save_packet (self):
        self._tail = (self._tail + 1) % QUEUE_SIZE

    def is_empty (self):
        return self._tail == self._head

    # Clear the queue. If requested, return the dequeued elements.
    def clear (self, dequeue = False):
        if not dequeue:
            self._head = self._tail
            return []

        pkts = [ ]
        while self._head != self._tail:
            pkts.append(self.pkt[self._head])
            self._head = (self._head + 1) % QUEUE_SIZE
        return pkts

class CollapseInfo:
    def __init__ (self):
        # Timestamp when collapsing begins
        self.time_sop = 0
        # The number of packets collapsed for each packet group
        self.count    = { SOF              : 0,
                          PING_NAK         : 0,
                          IN_ACK           : 0,
                          IN_NAK           : 0,
                          SPLIT_IN_ACK     : 0,
                          SPLIT_IN_NYET    : 0,
                          SPLIT_IN_NAK     : 0,
                          SPLIT_OUT_NYET   : 0,
                          SPLIT_SETUP_NYET : 0,
                          KEEP_ALIVE       : 0}

    def clear (self):
        self.time_sop = 0
        for k in self.count: self.count[k] = 0


#==========================================================================
# UTILITY FUNCTIONS
#==========================================================================
def timestamp_to_ns (stamp, samplerate_khz):
    return int((stamp * 1000) / (samplerate_khz/1000))

def print_general_status (status):
    """ General status codes """

    if (status == BG_READ_OK) :                  print "OK",
    if (status & BG_READ_TIMEOUT):               print "TIMEOUT",
    if (status & BG_READ_ERR_UNEXPECTED):        print "UNEXPECTED",
    if (status & BG_READ_ERR_MIDDLE_OF_PACKET):  print "MIDDLE",
    if (status & BG_READ_ERR_SHORT_BUFFER):      print "SHORT BUFFER",
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
    if (status & BG_READ_USB_TRUNCATION_MODE):   print "TRUNCATION_MODE;",
    if (status & BG_READ_USB_END_OF_CAPTURE):    print "END_OF_CAPTURE;",

def print_usb_events (events):
    """USB event codes"""
    if (events & BG_EVENT_USB_HOST_DISCONNECT):   print "HOST_DISCON;",
    if (events & BG_EVENT_USB_TARGET_DISCONNECT): print "TGT_DISCON;",
    if (events & BG_EVENT_USB_RESET):             print "RESET;",
    if (events & BG_EVENT_USB_HOST_CONNECT):      print "HOST_CONNECT;",
    if (events & BG_EVENT_USB_TARGET_CONNECT):    print "TGT_CONNECT/UNRST;",
    if (events & BG_EVENT_USB_DIGITAL_INPUT):     print "INPUT_TRIGGER %X" % \
       (events & BG_EVENT_USB_DIGITAL_INPUT_MASK),
    if (events & BG_EVENT_USB_CHIRP_J):           print "CHIRP_J; ",
    if (events & BG_EVENT_USB_CHIRP_K):           print "CHIRP_K; ",
    if (events & BG_EVENT_USB_KEEP_ALIVE):        print "KEEP_ALIVE; ",
    if (events & BG_EVENT_USB_SUSPEND):           print "SUSPEND; ",
    if (events & BG_EVENT_USB_RESUME):            print "RESUME; ",
    if (events & BG_EVENT_USB_LOW_SPEED):         print "LOW_SPEED; ",
    if (events & BG_EVENT_USB_FULL_SPEED):        print "FULL_SPEED; ",
    if (events & BG_EVENT_USB_HIGH_SPEED):        print "HIGH_SPEED; ",
    if (events & BG_EVENT_USB_SPEED_UNKNOWN):     print "UNKNOWN_SPEED; ",
    if (events & BG_EVENT_USB_LOW_OVER_FULL_SPEED):
        print "LOW_OVER_FULL_SPEED; ",

def usb_print_summary (i, count_sop, summary):
    count_sop_ns =  timestamp_to_ns(count_sop, samplerate_khz)
    print "%d,%u,USB,( ),%s" % (i, count_sop_ns, summary)

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

# Print common packet header information
def usb_print_packet (packet_number, packet, error_status):
    if (error_status == 0):
        error_status = ""
        packet_data  = usb_print_data_packet(packet.data, packet.length)
    else:
        packet_data = ""

    sys.stdout.write("%d,%u,USB,(%s " % (packet_number, packet.time_sop_ns,
                                         error_status))
    print_general_status(packet.status)
    print_usb_status(packet.status)
    print_usb_events(packet.events)

    print "),%s" % packet_data
    sys.stdout.flush()

# Dump saved summary information
def usb_print_summary_packet (packet_number, collapse_info, signal_errors):
    asdf
    offset  = 0
    summary = ""

    counts = [ collapse_info.count[key]
               for key in collapse_info.count
               if collapse_info.count[key] > 0 ]

    if ( len(counts) > 0):
        summary +=  "COLLAPSED "

        if (collapse_info.count[KEEP_ALIVE] > 0):
            summary += "[%d KEEP-ALIVE] " %  \
                       collapse_info.count[KEEP_ALIVE]

        if (collapse_info.count[SOF] > 0):
            summary += "[%d SOF] " %  \
                       collapse_info.count[SOF]

        if (collapse_info.count[IN_ACK] > 0):
            summary += "[%d IN/ACK] " % \
                       collapse_info.count[IN_ACK]

        if (collapse_info.count[IN_NAK] > 0):
            summary += "[%d IN/NAK] " % \
                       collapse_info.count[IN_NAK]

        if (collapse_info.count[PING_NAK] > 0):
            summary += "[%d PING/NAK] " % \
                       collapse_info.count[PING_NAK]

        if COMBINE_SPLITS:
            split_count = collapse_info.count[SPLIT_IN_ACK]   + \
                          collapse_info.count[SPLIT_IN_NYET]  + \
                          collapse_info.count[SPLIT_IN_NAK]   + \
                          collapse_info.count[SPLIT_OUT_NYET] + \
                          collapse_info.count[SPLIT_SETUP_NYET]

            if split_count > 0:
                summary += "[%d SPLITS] " % split_count
        else:
            if (collapse_info.count[SPLIT_IN_ACK] > 0):
                summary += "[%d SPLIT/IN/ACK] " % \
                           collapse_info.count[SPLIT_IN_ACK]

            if (collapse_info.count[SPLIT_IN_NYET] > 0):
                summary += "[%d SPLIT/IN/NYET] " % \
                           collapse_info.count[SPLIT_IN_NYET]

            if (collapse_info.count[SPLIT_IN_NAK] > 0):
                summary += "[%d SPLIT/IN/NAK] " % \
                           collapse_info.count[SPLIT_IN_NAK]

            if (collapse_info.count[SPLIT_OUT_NYET] > 0):
                summary += "[%d SPLIT/OUT/NYET] " % \
                           collapse_info.count[SPLIT_OUT_NYET]

            if (collapse_info.count[SPLIT_SETUP_NYET] > 0):
                summary += "[%d SPLIT/SETUP/NYET] " % \
                           collapse_info.count[SPLIT_SETUP_NYET]

        usb_print_summary(packet_number+offset, collapse_info.time_sop,
                          summary)
        offset += 1

    # Output any signal errors
    if (signal_errors > 0):
        summary += "<%d SIGNAL ERRORS>" %  signal_errors
        usb_print_summary(packet_number+offset, collapse_info.time_sop,
                          summary)
        offset += 1

    collapse_info.clear()
    return (packet_number + offset, 0)

# Outputs any packets saved during the collapsing process
def output_saved (packetnum, signal_errors, collapse_info, pkt_q):
    # (packetnum, signal_errors) = usb_print_summary_packet(packetnum, collapse_info, signal_errors)

    pkts = pkt_q.clear(dequeue = True)

    for pkt in pkts:
        bluetooth_process_usb_packet(pkt.time_sop_ns, pkt.data, pkt.length)
        # usb_print_packet(packetnum, pkt, 0)
        packetnum += 1

    return (packetnum, signal_errors)

# Collapses a group of packets.  This involves incrementing the group
# counter and clearing the queue. If this is the first group to
# be collapsed, the collapse time needs to be set, which marks when
# this collapsing began.
def collapse (group, collapse_info, pkt_q):
    collapse_info.count[group] += 1

    if collapse_info.time_sop == 0:
        if not pkt_q.is_empty:
            collapse_info.time_sop = pkt_q.head.time_sop
        else:
            collapse_info.time_sop = pkt_q.tail.time_sop

    pkt_q.clear()

# The main packet dump routine
def usb_dump ():
    # Collapsing counts and the time the collapsing started
    collapse_info = CollapseInfo()

    # Packets are saved during the collapsing process
    pkt_q = PacketQueue()

    pid           = 0
    signal_errors = 0
    packetnum     = 0

    # Collapsing packets is handled through a state machine.
    # IDLE is the initial state.
    state = IDLE

    global samplerate_khz
    samplerate_khz = bg_samplerate(beagle, 0)
    idle_samples   = IDLE_THRESHOLD * samplerate_khz

    # Configure Beagle 480 for realtime capture
    bg_usb2_capture_config(beagle, BG_USB2_CAPTURE_REALTIME)
    bg_usb2_target_config(beagle, BG_USB2_AUTO_SPEED_DETECT)
    bg_usb_configure(beagle, BG_USB_CAPTURE_USB2, BG_USB_TRIGGER_MODE_IMMEDIATE)

    # Filter out our own packets.  This is only relevant when
    # one host controller is used.
    bg_usb2_hw_filter_config(beagle,
                               BG_USB2_HW_FILTER_SELF)

    # Open the connection to the Beagle.  Default to port 0.
    if (bg_enable(beagle, BG_PROTOCOL_USB) != BG_OK):
        print "error: could not enable USB capture; exiting..."
        sys.exit(1)

    # Output the header...
    # print "index,time(ns),USB,status,pid,data0 ... dataN(*)"
    # sys.stdout.flush()

    # ...then start decoding packets
    while True:
        # Info for the current packet
        cur_packet = pkt_q.tail

        ( cur_packet.length, cur_packet.status, cur_packet.events ,
          cur_packet.time_sop, cur_packet.time_duration,
          cur_packet.time_dataoffset, cur_packet.data ) = \
          bg_usb2_read(beagle, cur_packet.data)

        cur_packet.time_sop_ns =  timestamp_to_ns(cur_packet.time_sop,
                                                 samplerate_khz)

        # Exit if observed end of capture
        if cur_packet.status & BG_READ_USB_END_OF_CAPTURE:
            usb_print_summary_packet(packetnum, collapse_info, signal_errors)
            break

        # Check for invalid packet or Beagle error
        if cur_packet.length < 0:
            error_status = "error=%d" % cur_packet.length
            usb_print_packet(packetnum, cur_packet, error_status)
            break

        # Check for USB error
        if cur_packet.status == BG_READ_USB_ERR_BAD_SIGNALS:
            signal_errors += 1

        # Set the PID for collapsing state machine below.  Treat
        # KEEP_ALIVEs as packets.
        if cur_packet.length > 0:
            pid = cur_packet.data[0]
        elif cur_packet.events & BG_EVENT_USB_KEEP_ALIVE and \
                 not cur_packet.status & BG_READ_USB_ERR_BAD_PID:
            pid = KEEP_ALIVE
        else:
            pid = 0

        # Collapse these packets approprietly:
        # SOF* (IN (ACK|NAK))* (PING NAK)*
        # (SPLIT (OUT|SETUP) NYET)* (SPLIT IN (ACK|NYET|NACK))*

        # If the time elapsed since collapsing began is greater than
        # the threshold, output the counts and zero out the counters.
        if cur_packet.time_sop - collapse_info.time_sop >= idle_samples:
            # (packetnum, signal_errors) = usb_print_summary_packet(packetnum, collapse_info, signal_errors)
            pass

        while True:
            re_run = False

            # The initial state of the state machine.  Collapse SOFs
            # and KEEP_ALIVEs.  Save IN, PING, or SPLIT packets and
            # move to the next state for the next packet.  Otherwise,
            # print the collapsed packet counts and the current packet.
            if state == IDLE:
                if pid == KEEP_ALIVE:
                    collapse(KEEP_ALIVE, collapse_info, pkt_q)
                elif pid == BG_USB_PID_SOF:
                    collapse(SOF, collapse_info, pkt_q)
                elif pid == BG_USB_PID_IN:
                    pkt_q.save_packet()
                    state = IN
                elif pid == BG_USB_PID_PING:
                    pkt_q.save_packet()
                    state = PING
                elif pid == BG_USB_PID_SPLIT:
                    pkt_q.save_packet()
                    state = SPLIT
                else:
                    # (packetnum, signal_errors) = usb_print_summary_packet(packetnum, collapse_info, signal_errors)

                    if (cur_packet.length > 0 or cur_packet.events or
                        (cur_packet.status != 0 and
                         cur_packet.status != BG_READ_TIMEOUT)):
                        bluetooth_process_usb_packet(cur_packet.time_sop_ns, cur_packet.data, cur_packet.length)
                        # usb_print_packet(packetnum, cur_packet, 0)
                        packetnum += 1

            # Collapsing IN+ACK or IN+NAK.  Otherwise, output any
            # saved packets and rerun the collapsing state machine
            # on the current packet.
            elif state == IN:
                state = IDLE
                if pid == BG_USB_PID_ACK:
                    collapse(IN_ACK, collapse_info, pkt_q)
                elif pid == BG_USB_PID_NAK:
                    collapse(IN_NAK, collapse_info, pkt_q)
                else:
                    re_run = True

            # Collapsing PING+NAK
            elif state == PING:
                state = IDLE
                if pid == BG_USB_PID_NAK:
                    collapse(PING_NAK, collapse_info, pkt_q)
                else:
                    re_run = True

            # Expecting an IN, OUT, or SETUP
            elif state == SPLIT:
                if pid == BG_USB_PID_IN:
                    pkt_q.save_packet()
                    state = SPLIT_IN
                elif pid == BG_USB_PID_OUT:
                    pkt_q.save_packet()
                    state = SPLIT_OUT
                elif pid == BG_USB_PID_SETUP:
                    pkt_q.save_packet()
                    state = SPLIT_SETUP
                else:
                    state = IDLE
                    re_run = True

            # Collapsing SPLIT+IN+NYET, SPLIT+IN+NAK, SPLIT+IN+ACK
            elif state == SPLIT_IN:
                state = IDLE
                if pid == BG_USB_PID_NYET:
                    collapse(SPLIT_IN_NYET, collapse_info, pkt_q)
                elif pid == BG_USB_PID_NAK:
                    collapse(SPLIT_IN_NAK, collapse_info, pkt_q)
                elif pid == BG_USB_PID_ACK:
                    collapse(SPLIT_IN_ACK, collapse_info, pkt_q)
                else:
                    re_run = True

            # Collapsing SPLIT+OUT+NYET
            elif state == SPLIT_OUT:
                state = IDLE
                if pid == BG_USB_PID_NYET:
                    collapse(SPLIT_OUT_NYET, collapse_info, pkt_q)
                else:
                    re_run = True

            # Collapsing SPLIT+SETUP+NYET
            elif state == SPLIT_SETUP:
                state = IDLE
                if pid == BG_USB_PID_NYET:
                    collapse(SPLIT_SETUP_NYET, collapse_info, pkt_q)
                else:
                    re_run = True

            if re_run == False:
                break

            # The state machine is about to be re-run.  This
            # means that a complete packet sequence wasn't collapsed
            # and there are packets in the queue that need to be
            # output before we can process the current packet.
            (packetnum, signal_errors) = \
                        output_saved(packetnum, signal_errors,
                                     collapse_info, pkt_q)

    # Stop the capture
    bg_disable(beagle)


#=========================================================================
# DIGITAL INPIT/OUTPUT CONFIG
# ========================================================================
def setup_digital_lines ():
    # Digital input mask
    input_enable_mask = \
               BG_USB2_DIGITAL_IN_ENABLE_PIN1 | \
               BG_USB2_DIGITAL_IN_ENABLE_PIN2 | \
               BG_USB2_DIGITAL_IN_ENABLE_PIN3 | \
               BG_USB2_DIGITAL_IN_ENABLE_PIN4

    packet_match = BeagleUsb2PacketMatch()
    data_match   = BeagleUsb2DataMatch()

    # Enable digital input pins
    bg_usb2_digital_in_config(beagle, input_enable_mask)
    print "Configuring digital input with %x" % input_enable_mask

    # Configure digital out pins.  The structures are initialized to
    # zero so only the fields that we want enabled need to be set.
    packet_match.pid_match_type = BG_USB2_MATCH_TYPE_EQUAL
    packet_match.pid_match_val  = BG_USB_PID_SETUP

    # Enable digital output pin 4
    bg_usb2_digital_out_config(beagle,
                               BG_USB2_DIGITAL_OUT_ENABLE_PIN4,
                               BG_USB2_DIGITAL_OUT_PIN4_ACTIVE_HIGH)

    # Configure digital output pin 4 match pattern
    bg_usb2_digital_out_match(beagle,
                              BG_USB2_DIGITAL_OUT_MATCH_PIN4,
                              packet_match, data_match)

    print "Configuring digital output pin 4."

#==========================================================================
# MAIN PROGRAM ENTRY POINT
#==========================================================================
port       = 0      # open port 0 by default
samplerate = 0      # in kHz (query)
timeout    = 500    # in milliseconds
latency    = 200    # in milliseconds

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

print "Host interface is %s." % \
      (bg_host_ifce_speed(beagle) and "high speed" or "full speed")

# Setup the digital input and output lines.
setup_digital_lines()

print ""
sys.stdout.flush()

# open hci_dump.pklg
with open ('hci_dump.pklg', 'wb') as fout:
    hci_dump_fout = fout
    usb_dump()

# Close the device
bg_close(beagle)

sys.exit(0)
