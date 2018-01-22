#==========================================================================
# Beagle Interface Library
#--------------------------------------------------------------------------
# Copyright (c) 2004-2011 Total Phase, Inc.
# All rights reserved.
# www.totalphase.com
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# - Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
# - Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
# - Neither the name of Total Phase, Inc. nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
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
#--------------------------------------------------------------------------
# To access Total Phase Beagle devices through the API:
#
# 1) Use one of the following shared objects:
#      beagle.so        --  Linux shared object
#          or
#      beagle.dll       --  Windows dynamic link library
#
# 2) Along with one of the following language modules:
#      beagle.c/h       --  C/C++ API header file and interface module
#      beagle_py.py     --  Python API
#      beagle.bas       --  Visual Basic 6 API
#      beagle.cs        --  C# .NET source
#      beagle_net.dll   --  Compiled .NET binding
#==========================================================================


#==========================================================================
# VERSION
#==========================================================================
BG_API_VERSION    = 0x050a   # v5.10
BG_REQ_SW_VERSION = 0x050a   # v5.10

import os
import sys
try:
    import beagle as api
except ImportError, ex1:
    import imp, platform, struct
    # pick system, 32/64, and extension
    system = "linux"
    architecture = "x86_64"
    extension = '.so'
    if platform.system() in ['Windows', 'Microsoft']:
        system = 'windows'
        extension = '.dll'
    elif platform.system() in ('Darwin'):
        system = 'macosx'
    if struct.calcsize('P') * 8 == 32:
        architecture = 'i686'
    lib_folder = system + '-' + architecture
    print("Library folder: %s" % lib_folder)

    try:
        api = imp.load_dynamic('beagle', lib_folder + '/beagle' + extension)
    except ImportError, ex2:
        import_err_msg  = 'Error importing beagle%s\n' % ext
        import_err_msg += '  Architecture of beagle%s may be wrong\n' % ext
        import_err_msg += '%s\n%s' % (ex1, ex2)
        raise ImportError(import_err_msg)

BG_SW_VERSION      = api.py_version() & 0xffff
BG_REQ_API_VERSION = (api.py_version() >> 16) & 0xffff
BG_LIBRARY_LOADED  = \
    ((BG_SW_VERSION >= BG_REQ_SW_VERSION) and \
     (BG_API_VERSION >= BG_REQ_API_VERSION))

from array import array, ArrayType
import struct


#==========================================================================
# HELPER FUNCTIONS
#==========================================================================
def array_u08 (n):  return array('B', '\0'*n)
def array_u16 (n):  return array('H', '\0\0'*n)
def array_u32 (n):  return array('I', '\0\0\0\0'*n)
def array_u64 (n):  return array('K', '\0\0\0\0\0\0\0\0'*n)
def array_s08 (n):  return array('b', '\0'*n)
def array_s16 (n):  return array('h', '\0\0'*n)
def array_s32 (n):  return array('i', '\0\0\0\0'*n)
def array_s64 (n):  return array('L', '\0\0\0\0\0\0\0\0'*n)
def array_f32 (n):  return array('f', '\0\0\0\0'*n)
def array_f64 (n):  return array('d', '\0\0\0\0\0\0\0\0'*n)


#==========================================================================
# STATUS CODES
#==========================================================================
# All API functions return an integer which is the result of the
# transaction, or a status code if negative.  The status codes are
# defined as follows:
# enum BeagleStatus
# General codes (0 to -99)
BG_OK                                          =    0
BG_UNABLE_TO_LOAD_LIBRARY                      =   -1
BG_UNABLE_TO_LOAD_DRIVER                       =   -2
BG_UNABLE_TO_LOAD_FUNCTION                     =   -3
BG_INCOMPATIBLE_LIBRARY                        =   -4
BG_INCOMPATIBLE_DEVICE                         =   -5
BG_INCOMPATIBLE_DRIVER                         =   -6
BG_COMMUNICATION_ERROR                         =   -7
BG_UNABLE_TO_OPEN                              =   -8
BG_UNABLE_TO_CLOSE                             =   -9
BG_INVALID_HANDLE                              =  -10
BG_CONFIG_ERROR                                =  -11
BG_UNKNOWN_PROTOCOL                            =  -12
BG_STILL_ACTIVE                                =  -13
BG_FUNCTION_NOT_AVAILABLE                      =  -14
BG_INVALID_LICENSE                             =  -15
BG_CAPTURE_NOT_TRIGGERED                       =  -16
BG_CAPTURE_NOT_READY_FOR_DOWNLOAD              =  -17

# COMMTEST codes (-100 to -199)
BG_COMMTEST_NOT_AVAILABLE                      = -100
BG_COMMTEST_NOT_ENABLED                        = -101

# I2C codes (-200 to -299)
BG_I2C_NOT_AVAILABLE                           = -200
BG_I2C_NOT_ENABLED                             = -201

# SPI codes (-300 to -399)
BG_SPI_NOT_AVAILABLE                           = -300
BG_SPI_NOT_ENABLED                             = -301

# USB codes (-400 to -499)
BG_USB_NOT_AVAILABLE                           = -400
BG_USB_NOT_ENABLED                             = -401
BG_USB2_NOT_ENABLED                            = -402
BG_USB3_NOT_ENABLED                            = -403

# Cross-Analyzer Sync codes (-410 to -413)
BG_CROSS_ANALYZER_SYNC_DISTURBED_RE_ENABLE     = -410
BG_CROSS_ANALYZER_SYNC_DISTURBED_RECONNECT     = -411
BG_CROSS_ANALYZER_SYNC_UNLICENSED_SELF         = -412
BG_CROSS_ANALYZER_SYNC_UNLICENSED_OTHER        = -413

# Complex Triggering Config codes (-450 to -469)
BG_COMPLEX_CONFIG_ERROR_NO_STATES              = -450
BG_COMPLEX_CONFIG_ERROR_DATA_PACKET_TYPE       = -451
BG_COMPLEX_CONFIG_ERROR_DATA_FIELD             = -452
BG_COMPLEX_CONFIG_ERROR_ERR_MATCH_FIELD        = -453
BG_COMPLEX_CONFIG_ERROR_DATA_RESOURCES         = -454
BG_COMPLEX_CONFIG_ERROR_DP_MATCH_TYPE          = -455
BG_COMPLEX_CONFIG_ERROR_DP_MATCH_VAL           = -456
BG_COMPLEX_CONFIG_ERROR_DP_REQUIRED            = -457
BG_COMPLEX_CONFIG_ERROR_DP_RESOURCES           = -458
BG_COMPLEX_CONFIG_ERROR_TIMER_UNIT             = -459
BG_COMPLEX_CONFIG_ERROR_TIMER_BOUNDS           = -460
BG_COMPLEX_CONFIG_ERROR_ASYNC_EVENT            = -461
BG_COMPLEX_CONFIG_ERROR_ASYNC_EDGE             = -462
BG_COMPLEX_CONFIG_ERROR_ACTION_FILTER          = -463
BG_COMPLEX_CONFIG_ERROR_ACTION_GOTO_SEL        = -464
BG_COMPLEX_CONFIG_ERROR_ACTION_GOTO_DEST       = -465
BG_COMPLEX_CONFIG_ERROR_BAD_VBUS_TRIGGER_TYPE  = -466
BG_COMPLEX_CONFIG_ERROR_BAD_VBUS_TRIGGER_THRES = -467
BG_COMPLEX_CONFIG_ERROR_NO_MULTI_VBUS_TRIGGERS = -468
BG_COMPLEX_CONFIG_ERROR_IV_MONITOR_NOT_ENABLED = -469

# MDIO codes (-500 to -599)
BG_MDIO_NOT_AVAILABLE                          = -500
BG_MDIO_NOT_ENABLED                            = -501
BG_MDIO_BAD_TURNAROUND                         = -502

# IV MON codes (-600 to -699)
BG_IV_MON_NULL_PACKET                          = -600
BG_IV_MON_INVALID_PACKET_LENGTH                = -601


#==========================================================================
# GENERAL TYPE DEFINITIONS
#==========================================================================
# Beagle handle type definition
# typedef Beagle => integer

# Beagle version matrix.
#
# This matrix describes the various version dependencies
# of Beagle components.  It can be used to determine
# which component caused an incompatibility error.
#
# All version numbers are of the format:
#   (major << 8) | minor
#
# ex. v1.20 would be encoded as:  0x0114
class BeagleVersion:
    def __init__ (self):
        # Software, firmware, and hardware versions.
        self.software        = 0
        self.firmware        = 0
        self.hardware        = 0

        # Hardware revisions that are compatible with this software version.
        # The top 16 bits gives the maximum accepted hw revision.
        # The lower 16 bits gives the minimum accepted hw revision.
        self.hw_revs_for_sw  = 0

        # Firmware revisions that are compatible with this software version.
        # The top 16 bits gives the maximum accepted fw revision.
        # The lower 16 bits gives the minimum accepted fw revision.
        self.fw_revs_for_sw  = 0

        # Driver revisions that are compatible with this software version.
        # The top 16 bits gives the maximum accepted driver revision.
        # The lower 16 bits gives the minimum accepted driver revision.
        # This version checking is currently only pertinent for WIN32
        # platforms.
        self.drv_revs_for_sw = 0

        # Software requires that the API interface must be >= this version.
        self.api_req_by_sw   = 0


#==========================================================================
# GENERAL API
#==========================================================================
# Get a list of ports to which Beagle devices are attached.
#
# num_devices = maximum number of elements to return
# devices     = array into which the port numbers are returned
#
# Each element of the array is written with the port number.
# Devices that are in-use are ORed with BG_PORT_NOT_FREE
# (0x8000).
#
# ex.  devices are attached to ports 0, 1, 2
#      ports 0 and 2 are available, and port 1 is in-use.
#      array => 0x0000, 0x8001, 0x0002
#
# If the array is NULL, it is not filled with any values.
# If there are more devices than the array size, only the
# first nmemb port numbers will be written into the array.
#
# Returns the number of devices found, regardless of the
# array size.
BG_PORT_NOT_FREE = 0x8000
def bg_find_devices (devices):
    """usage: (int return, u16[] devices) = bg_find_devices(u16[] devices)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function.

    Additionally, for arrays that are filled by the API function, an
    integer can be passed in place of the array argument and the API
    will automatically create an array of that length.  All output
    arrays, whether passed in or generated, are passed back in the
    returned tuple."""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # devices pre-processing
    __devices = isinstance(devices, int)
    if __devices:
        (devices, num_devices) = (array_u16(devices), devices)
    else:
        (devices, num_devices) = isinstance(devices, ArrayType) and (devices, len(devices)) or (devices[0], min(len(devices[0]), int(devices[1])))
        if devices.typecode != 'H':
            raise TypeError("type for 'devices' must be array('H')")
    # Call API function
    (_ret_) = api.py_bg_find_devices(num_devices, devices)
    # devices post-processing
    if __devices: del devices[max(0, min(_ret_, len(devices))):]
    return (_ret_, devices)


# Get a list of ports to which Beagle devices are attached
#
# This function is the same as bg_find_devices() except that
# it returns the unique IDs of each Beagle device.  The IDs
# are guaranteed to be non-zero if valid.
#
# The IDs are the unsigned integer representation of the 10-digit
# serial numbers.
def bg_find_devices_ext (devices, unique_ids):
    """usage: (int return, u16[] devices, u32[] unique_ids) = bg_find_devices_ext(u16[] devices, u32[] unique_ids)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function.

    Additionally, for arrays that are filled by the API function, an
    integer can be passed in place of the array argument and the API
    will automatically create an array of that length.  All output
    arrays, whether passed in or generated, are passed back in the
    returned tuple."""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # devices pre-processing
    __devices = isinstance(devices, int)
    if __devices:
        (devices, num_devices) = (array_u16(devices), devices)
    else:
        (devices, num_devices) = isinstance(devices, ArrayType) and (devices, len(devices)) or (devices[0], min(len(devices[0]), int(devices[1])))
        if devices.typecode != 'H':
            raise TypeError("type for 'devices' must be array('H')")
    # unique_ids pre-processing
    __unique_ids = isinstance(unique_ids, int)
    if __unique_ids:
        (unique_ids, num_ids) = (array_u32(unique_ids), unique_ids)
    else:
        (unique_ids, num_ids) = isinstance(unique_ids, ArrayType) and (unique_ids, len(unique_ids)) or (unique_ids[0], min(len(unique_ids[0]), int(unique_ids[1])))
        if unique_ids.typecode != 'I':
            raise TypeError("type for 'unique_ids' must be array('I')")
    # Call API function
    (_ret_) = api.py_bg_find_devices_ext(num_devices, num_ids, devices, unique_ids)
    # devices post-processing
    if __devices: del devices[max(0, min(_ret_, len(devices))):]
    # unique_ids post-processing
    if __unique_ids: del unique_ids[max(0, min(_ret_, len(unique_ids))):]
    return (_ret_, devices, unique_ids)


# Open the Beagle port.
#
# The port number is a zero-indexed integer.
#
# The port number is the same as that obtained from the
# bg_find_devices() function above.
#
# Returns an Beagle handle, which is guaranteed to be
# greater than zero if it is valid.
#
# This function is recommended for use in simple applications
# where extended information is not required.  For more complex
# applications, the use of bg_open_ext() is recommended.
def bg_open (port_number):
    """usage: Beagle return = bg_open(int port_number)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_open(port_number)


# Open the Beagle port, returning extended information
# in the supplied structure.  Behavior is otherwise identical
# to bg_open() above.  If 0 is passed as the pointer to the
# structure, this function is exactly equivalent to bg_open().
#
# The structure is zeroed before the open is attempted.
# It is filled with whatever information is available.
#
# For example, if the hardware version is not filled, then
# the device could not be queried for its version number.
#
# This function is recommended for use in complex applications
# where extended information is required.  For more simple
# applications, the use of bg_open() is recommended.
class BeagleExt:
    def __init__ (self):
        # Version matrix
        self.version  = BeagleVersion()

        # Features of this device.
        self.features = 0

def bg_open_ext (port_number):
    """usage: (Beagle return, BeagleExt bg_ext) = bg_open_ext(int port_number)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    (_ret_, c_bg_ext) = api.py_bg_open_ext(port_number)
    # bg_ext post-processing
    bg_ext = BeagleExt()
    (bg_ext.version.software, bg_ext.version.firmware, bg_ext.version.hardware, bg_ext.version.hw_revs_for_sw, bg_ext.version.fw_revs_for_sw, bg_ext.version.drv_revs_for_sw, bg_ext.version.api_req_by_sw, bg_ext.features) = c_bg_ext
    return (_ret_, bg_ext)


# Close the Beagle port.
def bg_close (beagle):
    """usage: int return = bg_close(Beagle beagle)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_close(beagle)


# Return the port for this Beagle handle.
#
# The port number is a zero-indexed integer.
def bg_port (beagle):
    """usage: int return = bg_port(Beagle beagle)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_port(beagle)


# Return the device features as a bit-mask of values, or
# an error code if the handle is not valid.
BG_FEATURE_NONE = 0x00000000
BG_FEATURE_I2C = 0x00000001
BG_FEATURE_SPI = 0x00000002
BG_FEATURE_USB = 0x00000004
BG_FEATURE_MDIO = 0x00000008
BG_FEATURE_USB_HS = 0x00000010
BG_FEATURE_USB_SS = 0x00000020
def bg_features (beagle):
    """usage: int return = bg_features(Beagle beagle)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_features(beagle)


def bg_unique_id_to_features (unique_id):
    """usage: int return = bg_unique_id_to_features(u32 unique_id)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_unique_id_to_features(unique_id)


# Return the unique ID for this Beagle adapter.
# IDs are guaranteed to be non-zero if valid.
# The ID is the unsigned integer representation of the
# 10-digit serial number.
def bg_unique_id (beagle):
    """usage: u32 return = bg_unique_id(Beagle beagle)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_unique_id(beagle)


# Return the status string for the given status code.
# If the code is not valid or the library function cannot
# be loaded, return a NULL string.
def bg_status_string (status):
    """usage: str return = bg_status_string(int status)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_status_string(status)


# Return the version matrix for the device attached to the
# given handle.  If the handle is 0 or invalid, only the
# software and required api versions are set.
def bg_version (beagle):
    """usage: (int return, BeagleVersion version) = bg_version(Beagle beagle)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    (_ret_, c_version) = api.py_bg_version(beagle)
    # version post-processing
    version = BeagleVersion()
    (version.software, version.firmware, version.hardware, version.hw_revs_for_sw, version.fw_revs_for_sw, version.drv_revs_for_sw, version.api_req_by_sw) = c_version
    return (_ret_, version)


# Set the capture latency to the specified number of milliseconds.
# This number determines the minimum time that a read call will
# block if there is no available data.  Lower times result in
# faster turnaround at the expense of reduced buffering.  Setting
# this parameter too low can cause packets to be dropped.
def bg_latency (beagle, milliseconds):
    """usage: int return = bg_latency(Beagle beagle, u32 milliseconds)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_latency(beagle, milliseconds)


# Set the capture timeout to the specified number of milliseconds.
# If any read call has a longer idle than this value, that call
# will return with a count of 0 bytes.
def bg_timeout (beagle, milliseconds):
    """usage: int return = bg_timeout(Beagle beagle, u32 milliseconds)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_timeout(beagle, milliseconds)


# Sleep for the specified number of milliseconds
# Accuracy depends on the operating system scheduler
# Returns the number of milliseconds slept
def bg_sleep_ms (milliseconds):
    """usage: u32 return = bg_sleep_ms(u32 milliseconds)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_sleep_ms(milliseconds)


# Configure the target power pin.
BG_TARGET_POWER_OFF = 0x00
BG_TARGET_POWER_ON = 0x01
BG_TARGET_POWER_QUERY = 0x80
def bg_target_power (beagle, power_flag):
    """usage: int return = bg_target_power(Beagle beagle, u08 power_flag)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_target_power(beagle, power_flag)


BG_HOST_IFCE_FULL_SPEED = 0x00
BG_HOST_IFCE_HIGH_SPEED = 0x01
BG_HOST_IFCE_SUPER_SPEED = 0x02
def bg_host_ifce_speed (beagle):
    """usage: int return = bg_host_ifce_speed(Beagle beagle)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_host_ifce_speed(beagle)


# Returns the device address that the beagle is attached to.
def bg_dev_addr (beagle):
    """usage: int return = bg_dev_addr(Beagle beagle)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_dev_addr(beagle)



#==========================================================================
# BUFFERING API
#==========================================================================
# Set the amount of buffering that is to be allocated on the PC.
# Pass zero to num_bytes to query the existing buffer size.
def bg_host_buffer_size (beagle, num_bytes):
    """usage: int return = bg_host_buffer_size(Beagle beagle, u32 num_bytes)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_host_buffer_size(beagle, num_bytes)


# Query the amount of buffering that is unused and free for buffering.
def bg_host_buffer_free (beagle):
    """usage: int return = bg_host_buffer_free(Beagle beagle)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_host_buffer_free(beagle)


# Query the amount of buffering that is used and no longer available.
def bg_host_buffer_used (beagle):
    """usage: int return = bg_host_buffer_used(Beagle beagle)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_host_buffer_used(beagle)


# Benchmark the speed of the host to Beagle interface
def bg_commtest (beagle, num_samples, delay_count):
    """usage: int return = bg_commtest(Beagle beagle, int num_samples, int delay_count)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_commtest(beagle, num_samples, delay_count)



#==========================================================================
# MONITORING API
#==========================================================================
# Protocol codes
# enum BeagleProtocol
BG_PROTOCOL_NONE     = 0
BG_PROTOCOL_COMMTEST = 1
BG_PROTOCOL_USB      = 2
BG_PROTOCOL_I2C      = 3
BG_PROTOCOL_SPI      = 4
BG_PROTOCOL_MDIO     = 5

# Common Beagle read status codes
# PARTIAL_LAST_BYTE Unused by USB 480 and 5000
BG_READ_OK = 0x00000000
BG_READ_TIMEOUT = 0x00000100
BG_READ_ERR_MIDDLE_OF_PACKET = 0x00000200
BG_READ_ERR_SHORT_BUFFER = 0x00000400
BG_READ_ERR_PARTIAL_LAST_BYTE = 0x00000800
BG_READ_ERR_PARTIAL_LAST_BYTE_MASK = 0x0000000f
BG_READ_ERR_UNEXPECTED = 0x00001000
# Enable the Beagle monitor
def bg_enable (beagle, protocol):
    """usage: int return = bg_enable(Beagle beagle, BeagleProtocol protocol)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_enable(beagle, protocol)


# Disable the Beagle monitor
def bg_disable (beagle):
    """usage: int return = bg_disable(Beagle beagle)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_disable(beagle)


# Capture stop function only supported for analyzers with
# on-board triggering capability.  For other analyzers, use
# bg_disable to stop the capture and download to PC.
def bg_capture_stop (beagle):
    """usage: int return = bg_capture_stop(Beagle beagle)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_capture_stop(beagle)


def bg_capture_trigger (beagle):
    """usage: int return = bg_capture_trigger(Beagle beagle)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_capture_trigger(beagle)


# Capture status; general across protocols but used in
# protocol-specific capture-status-query functions as well
# enum BeagleCaptureStatus
BG_CAPTURE_STATUS_UNKNOWN          = -1
BG_CAPTURE_STATUS_INACTIVE         =  0
BG_CAPTURE_STATUS_SYNC_STANDBY     =  1
BG_CAPTURE_STATUS_PRE_TRIGGER      =  2
BG_CAPTURE_STATUS_PRE_TRIGGER_SYNC =  3
BG_CAPTURE_STATUS_POST_TRIGGER     =  4
BG_CAPTURE_STATUS_TRANSFER         =  5
BG_CAPTURE_STATUS_COMPLETE         =  6

def bg_capture_trigger_wait (beagle, timeout_ms):
    """usage: (int return, BeagleCaptureStatus status) = bg_capture_trigger_wait(Beagle beagle, u32 timeout_ms)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_capture_trigger_wait(beagle, timeout_ms)


# Set the sample rate in kilohertz.
def bg_samplerate (beagle, samplerate_khz):
    """usage: int return = bg_samplerate(Beagle beagle, int samplerate_khz)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_samplerate(beagle, samplerate_khz)


# Get the number of bits for the given number of bytes in the
# given protocol.
# Use this to determine how large a bit_timing array to allocate
# for bg_*_read_bit_timing functions.
def bg_bit_timing_size (protocol, num_data_bytes):
    """usage: int return = bg_bit_timing_size(BeagleProtocol protocol, int num_data_bytes)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_bit_timing_size(protocol, num_data_bytes)



#==========================================================================
# I2C API
#==========================================================================
# Configure the I2C pullup resistors.
BG_I2C_PULLUP_OFF = 0x00
BG_I2C_PULLUP_ON = 0x01
BG_I2C_PULLUP_QUERY = 0x80
def bg_i2c_pullup (beagle, pullup_flag):
    """usage: int return = bg_i2c_pullup(Beagle beagle, u08 pullup_flag)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_i2c_pullup(beagle, pullup_flag)


BG_I2C_MONITOR_DATA = 0x00ff
BG_I2C_MONITOR_NACK = 0x0100
BG_READ_I2C_NO_STOP = 0x00010000
def bg_i2c_read (beagle, data_in):
    """usage: (int return, u32 status, u64 time_sop, u64 time_duration, u32 time_dataoffset, u16[] data_in) = bg_i2c_read(Beagle beagle, u16[] data_in)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function.

    Additionally, for arrays that are filled by the API function, an
    integer can be passed in place of the array argument and the API
    will automatically create an array of that length.  All output
    arrays, whether passed in or generated, are passed back in the
    returned tuple."""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # data_in pre-processing
    __data_in = isinstance(data_in, int)
    if __data_in:
        (data_in, max_bytes) = (array_u16(data_in), data_in)
    else:
        (data_in, max_bytes) = isinstance(data_in, ArrayType) and (data_in, len(data_in)) or (data_in[0], min(len(data_in[0]), int(data_in[1])))
        if data_in.typecode != 'H':
            raise TypeError("type for 'data_in' must be array('H')")
    # Call API function
    (_ret_, status, time_sop, time_duration, time_dataoffset) = api.py_bg_i2c_read(beagle, max_bytes, data_in)
    # data_in post-processing
    if __data_in: del data_in[max(0, min(_ret_, len(data_in))):]
    return (_ret_, status, time_sop, time_duration, time_dataoffset, data_in)


def bg_i2c_read_data_timing (beagle, data_in, data_timing):
    """usage: (int return, u32 status, u64 time_sop, u64 time_duration, u32 time_dataoffset, u16[] data_in, u32[] data_timing) = bg_i2c_read_data_timing(Beagle beagle, u16[] data_in, u32[] data_timing)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function.

    Additionally, for arrays that are filled by the API function, an
    integer can be passed in place of the array argument and the API
    will automatically create an array of that length.  All output
    arrays, whether passed in or generated, are passed back in the
    returned tuple."""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # data_in pre-processing
    __data_in = isinstance(data_in, int)
    if __data_in:
        (data_in, max_bytes) = (array_u16(data_in), data_in)
    else:
        (data_in, max_bytes) = isinstance(data_in, ArrayType) and (data_in, len(data_in)) or (data_in[0], min(len(data_in[0]), int(data_in[1])))
        if data_in.typecode != 'H':
            raise TypeError("type for 'data_in' must be array('H')")
    # data_timing pre-processing
    __data_timing = isinstance(data_timing, int)
    if __data_timing:
        (data_timing, max_timing) = (array_u32(data_timing), data_timing)
    else:
        (data_timing, max_timing) = isinstance(data_timing, ArrayType) and (data_timing, len(data_timing)) or (data_timing[0], min(len(data_timing[0]), int(data_timing[1])))
        if data_timing.typecode != 'I':
            raise TypeError("type for 'data_timing' must be array('I')")
    # Call API function
    (_ret_, status, time_sop, time_duration, time_dataoffset) = api.py_bg_i2c_read_data_timing(beagle, max_bytes, max_timing, data_in, data_timing)
    # data_in post-processing
    if __data_in: del data_in[max(0, min(_ret_, len(data_in))):]
    # data_timing post-processing
    if __data_timing: del data_timing[max(0, min(_ret_, len(data_timing))):]
    return (_ret_, status, time_sop, time_duration, time_dataoffset, data_in, data_timing)


def bg_i2c_read_bit_timing (beagle, data_in, bit_timing):
    """usage: (int return, u32 status, u64 time_sop, u64 time_duration, u32 time_dataoffset, u16[] data_in, u32[] bit_timing) = bg_i2c_read_bit_timing(Beagle beagle, u16[] data_in, u32[] bit_timing)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function.

    Additionally, for arrays that are filled by the API function, an
    integer can be passed in place of the array argument and the API
    will automatically create an array of that length.  All output
    arrays, whether passed in or generated, are passed back in the
    returned tuple."""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # data_in pre-processing
    __data_in = isinstance(data_in, int)
    if __data_in:
        (data_in, max_bytes) = (array_u16(data_in), data_in)
    else:
        (data_in, max_bytes) = isinstance(data_in, ArrayType) and (data_in, len(data_in)) or (data_in[0], min(len(data_in[0]), int(data_in[1])))
        if data_in.typecode != 'H':
            raise TypeError("type for 'data_in' must be array('H')")
    # bit_timing pre-processing
    __bit_timing = isinstance(bit_timing, int)
    if __bit_timing:
        (bit_timing, max_timing) = (array_u32(bit_timing), bit_timing)
    else:
        (bit_timing, max_timing) = isinstance(bit_timing, ArrayType) and (bit_timing, len(bit_timing)) or (bit_timing[0], min(len(bit_timing[0]), int(bit_timing[1])))
        if bit_timing.typecode != 'I':
            raise TypeError("type for 'bit_timing' must be array('I')")
    # Call API function
    (_ret_, status, time_sop, time_duration, time_dataoffset) = api.py_bg_i2c_read_bit_timing(beagle, max_bytes, max_timing, data_in, bit_timing)
    # data_in post-processing
    if __data_in: del data_in[max(0, min(_ret_, len(data_in))):]
    # bit_timing post-processing
    if __bit_timing: del bit_timing[max(0, min(bg_bit_timing_size(BG_PROTOCOL_I2C, _ret_), len(bit_timing))):]
    return (_ret_, status, time_sop, time_duration, time_dataoffset, data_in, bit_timing)



#==========================================================================
# SPI API
#==========================================================================
# enum BeagleSpiSSPolarity
BG_SPI_SS_ACTIVE_LOW  = 0
BG_SPI_SS_ACTIVE_HIGH = 1

# enum BeagleSpiSckSamplingEdge
BG_SPI_SCK_SAMPLING_EDGE_RISING  = 0
BG_SPI_SCK_SAMPLING_EDGE_FALLING = 1

# enum BeagleSpiBitorder
BG_SPI_BITORDER_MSB = 0
BG_SPI_BITORDER_LSB = 1

def bg_spi_configure (beagle, ss_polarity, sck_sampling_edge, bitorder):
    """usage: int return = bg_spi_configure(Beagle beagle, BeagleSpiSSPolarity ss_polarity, BeagleSpiSckSamplingEdge sck_sampling_edge, BeagleSpiBitorder bitorder)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_spi_configure(beagle, ss_polarity, sck_sampling_edge, bitorder)


def bg_spi_read (beagle, data_mosi, data_miso):
    """usage: (int return, u32 status, u64 time_sop, u64 time_duration, u32 time_dataoffset, u08[] data_mosi, u08[] data_miso) = bg_spi_read(Beagle beagle, u08[] data_mosi, u08[] data_miso)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function.

    Additionally, for arrays that are filled by the API function, an
    integer can be passed in place of the array argument and the API
    will automatically create an array of that length.  All output
    arrays, whether passed in or generated, are passed back in the
    returned tuple."""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # data_mosi pre-processing
    __data_mosi = isinstance(data_mosi, int)
    if __data_mosi:
        (data_mosi, mosi_max_bytes) = (array_u08(data_mosi), data_mosi)
    else:
        (data_mosi, mosi_max_bytes) = isinstance(data_mosi, ArrayType) and (data_mosi, len(data_mosi)) or (data_mosi[0], min(len(data_mosi[0]), int(data_mosi[1])))
        if data_mosi.typecode != 'B':
            raise TypeError("type for 'data_mosi' must be array('B')")
    # data_miso pre-processing
    __data_miso = isinstance(data_miso, int)
    if __data_miso:
        (data_miso, miso_max_bytes) = (array_u08(data_miso), data_miso)
    else:
        (data_miso, miso_max_bytes) = isinstance(data_miso, ArrayType) and (data_miso, len(data_miso)) or (data_miso[0], min(len(data_miso[0]), int(data_miso[1])))
        if data_miso.typecode != 'B':
            raise TypeError("type for 'data_miso' must be array('B')")
    # Call API function
    (_ret_, status, time_sop, time_duration, time_dataoffset) = api.py_bg_spi_read(beagle, mosi_max_bytes, miso_max_bytes, data_mosi, data_miso)
    # data_mosi post-processing
    if __data_mosi: del data_mosi[max(0, min(_ret_, len(data_mosi))):]
    # data_miso post-processing
    if __data_miso: del data_miso[max(0, min(_ret_, len(data_miso))):]
    return (_ret_, status, time_sop, time_duration, time_dataoffset, data_mosi, data_miso)


def bg_spi_read_data_timing (beagle, data_mosi, data_miso, data_timing):
    """usage: (int return, u32 status, u64 time_sop, u64 time_duration, u32 time_dataoffset, u08[] data_mosi, u08[] data_miso, u32[] data_timing) = bg_spi_read_data_timing(Beagle beagle, u08[] data_mosi, u08[] data_miso, u32[] data_timing)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function.

    Additionally, for arrays that are filled by the API function, an
    integer can be passed in place of the array argument and the API
    will automatically create an array of that length.  All output
    arrays, whether passed in or generated, are passed back in the
    returned tuple."""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # data_mosi pre-processing
    __data_mosi = isinstance(data_mosi, int)
    if __data_mosi:
        (data_mosi, mosi_max_bytes) = (array_u08(data_mosi), data_mosi)
    else:
        (data_mosi, mosi_max_bytes) = isinstance(data_mosi, ArrayType) and (data_mosi, len(data_mosi)) or (data_mosi[0], min(len(data_mosi[0]), int(data_mosi[1])))
        if data_mosi.typecode != 'B':
            raise TypeError("type for 'data_mosi' must be array('B')")
    # data_miso pre-processing
    __data_miso = isinstance(data_miso, int)
    if __data_miso:
        (data_miso, miso_max_bytes) = (array_u08(data_miso), data_miso)
    else:
        (data_miso, miso_max_bytes) = isinstance(data_miso, ArrayType) and (data_miso, len(data_miso)) or (data_miso[0], min(len(data_miso[0]), int(data_miso[1])))
        if data_miso.typecode != 'B':
            raise TypeError("type for 'data_miso' must be array('B')")
    # data_timing pre-processing
    __data_timing = isinstance(data_timing, int)
    if __data_timing:
        (data_timing, max_timing) = (array_u32(data_timing), data_timing)
    else:
        (data_timing, max_timing) = isinstance(data_timing, ArrayType) and (data_timing, len(data_timing)) or (data_timing[0], min(len(data_timing[0]), int(data_timing[1])))
        if data_timing.typecode != 'I':
            raise TypeError("type for 'data_timing' must be array('I')")
    # Call API function
    (_ret_, status, time_sop, time_duration, time_dataoffset) = api.py_bg_spi_read_data_timing(beagle, mosi_max_bytes, miso_max_bytes, max_timing, data_mosi, data_miso, data_timing)
    # data_mosi post-processing
    if __data_mosi: del data_mosi[max(0, min(_ret_, len(data_mosi))):]
    # data_miso post-processing
    if __data_miso: del data_miso[max(0, min(_ret_, len(data_miso))):]
    # data_timing post-processing
    if __data_timing: del data_timing[max(0, min(_ret_, len(data_timing))):]
    return (_ret_, status, time_sop, time_duration, time_dataoffset, data_mosi, data_miso, data_timing)


def bg_spi_read_bit_timing (beagle, data_mosi, data_miso, bit_timing):
    """usage: (int return, u32 status, u64 time_sop, u64 time_duration, u32 time_dataoffset, u08[] data_mosi, u08[] data_miso, u32[] bit_timing) = bg_spi_read_bit_timing(Beagle beagle, u08[] data_mosi, u08[] data_miso, u32[] bit_timing)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function.

    Additionally, for arrays that are filled by the API function, an
    integer can be passed in place of the array argument and the API
    will automatically create an array of that length.  All output
    arrays, whether passed in or generated, are passed back in the
    returned tuple."""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # data_mosi pre-processing
    __data_mosi = isinstance(data_mosi, int)
    if __data_mosi:
        (data_mosi, mosi_max_bytes) = (array_u08(data_mosi), data_mosi)
    else:
        (data_mosi, mosi_max_bytes) = isinstance(data_mosi, ArrayType) and (data_mosi, len(data_mosi)) or (data_mosi[0], min(len(data_mosi[0]), int(data_mosi[1])))
        if data_mosi.typecode != 'B':
            raise TypeError("type for 'data_mosi' must be array('B')")
    # data_miso pre-processing
    __data_miso = isinstance(data_miso, int)
    if __data_miso:
        (data_miso, miso_max_bytes) = (array_u08(data_miso), data_miso)
    else:
        (data_miso, miso_max_bytes) = isinstance(data_miso, ArrayType) and (data_miso, len(data_miso)) or (data_miso[0], min(len(data_miso[0]), int(data_miso[1])))
        if data_miso.typecode != 'B':
            raise TypeError("type for 'data_miso' must be array('B')")
    # bit_timing pre-processing
    __bit_timing = isinstance(bit_timing, int)
    if __bit_timing:
        (bit_timing, max_timing) = (array_u32(bit_timing), bit_timing)
    else:
        (bit_timing, max_timing) = isinstance(bit_timing, ArrayType) and (bit_timing, len(bit_timing)) or (bit_timing[0], min(len(bit_timing[0]), int(bit_timing[1])))
        if bit_timing.typecode != 'I':
            raise TypeError("type for 'bit_timing' must be array('I')")
    # Call API function
    (_ret_, status, time_sop, time_duration, time_dataoffset) = api.py_bg_spi_read_bit_timing(beagle, mosi_max_bytes, miso_max_bytes, max_timing, data_mosi, data_miso, bit_timing)
    # data_mosi post-processing
    if __data_mosi: del data_mosi[max(0, min(_ret_, len(data_mosi))):]
    # data_miso post-processing
    if __data_miso: del data_miso[max(0, min(_ret_, len(data_miso))):]
    # bit_timing post-processing
    if __bit_timing: del bit_timing[max(0, min(bg_bit_timing_size(BG_PROTOCOL_SPI, _ret_), len(bit_timing))):]
    return (_ret_, status, time_sop, time_duration, time_dataoffset, data_mosi, data_miso, bit_timing)



#==========================================================================
# USB API
#==========================================================================
# USB packet PID definitions
BG_USB_PID_OUT = 0xe1
BG_USB_PID_IN = 0x69
BG_USB_PID_SOF = 0xa5
BG_USB_PID_SETUP = 0x2d
BG_USB_PID_DATA0 = 0xc3
BG_USB_PID_DATA1 = 0x4b
BG_USB_PID_DATA2 = 0x87
BG_USB_PID_MDATA = 0x0f
BG_USB_PID_ACK = 0xd2
BG_USB_PID_NAK = 0x5a
BG_USB_PID_STALL = 0x1e
BG_USB_PID_NYET = 0x96
BG_USB_PID_PRE = 0x3c
BG_USB_PID_ERR = 0x3c
BG_USB_PID_SPLIT = 0x78
BG_USB_PID_PING = 0xb4
BG_USB_PID_EXT = 0xf0
BG_USB_PID_CORRUPTED = 0xff
# The following codes are returned for USB 12, 480, and 5000 captures
BG_READ_USB_ERR_BAD_SIGNALS = 0x00010000
BG_READ_USB_ERR_BAD_PID = 0x00200000
BG_READ_USB_ERR_BAD_CRC = 0x00400000
# The following codes are only returned for USB 12 captures
BG_READ_USB_ERR_BAD_SYNC = 0x00020000
BG_READ_USB_ERR_BIT_STUFF = 0x00040000
BG_READ_USB_ERR_FALSE_EOP = 0x00080000
BG_READ_USB_ERR_LONG_EOP = 0x00100000
# The following codes are only returned for USB 480 and 5000  captures
BG_READ_USB_TRUNCATION_LEN_MASK = 0x000000ff
BG_READ_USB_TRUNCATION_MODE = 0x20000000
BG_READ_USB_END_OF_CAPTURE = 0x40000000
# The following codes are only returned for USB 5000 captures
BG_READ_USB_ERR_BAD_SLC_CRC_1 = 0x00008000
BG_READ_USB_ERR_BAD_SLC_CRC_2 = 0x00010000
BG_READ_USB_ERR_BAD_SHP_CRC_16 = 0x00008000
BG_READ_USB_ERR_BAD_SHP_CRC_5 = 0x00010000
BG_READ_USB_ERR_BAD_SDP_CRC = 0x00008000
BG_READ_USB_EDB_FRAMING = 0x00020000
BG_READ_USB_ERR_UNK_END_OF_FRAME = 0x00040000
BG_READ_USB_ERR_DATA_LEN_INVALID = 0x00080000
BG_READ_USB_PKT_TYPE_LINK = 0x00100000
BG_READ_USB_PKT_TYPE_HDR = 0x00200000
BG_READ_USB_PKT_TYPE_DP = 0x00400000
BG_READ_USB_PKT_TYPE_TSEQ = 0x00800000
BG_READ_USB_PKT_TYPE_TS1 = 0x01000000
BG_READ_USB_PKT_TYPE_TS2 = 0x02000000
BG_READ_USB_ERR_BAD_TS = 0x04000000
BG_READ_USB_ERR_FRAMING = 0x08000000
# The following events are returned for USB 12, 480, and 5000 captures
BG_EVENT_USB_HOST_DISCONNECT = 0x00000100
BG_EVENT_USB_TARGET_DISCONNECT = 0x00000200
BG_EVENT_USB_HOST_CONNECT = 0x00000400
BG_EVENT_USB_TARGET_CONNECT = 0x00000800
BG_EVENT_USB_RESET = 0x00001000
# USB 480 and 5000 specific event codes
# USB 2.0
BG_EVENT_USB_DIGITAL_INPUT_MASK = 0x0000000f
BG_EVENT_USB_CHIRP_J = 0x00002000
BG_EVENT_USB_CHIRP_K = 0x00004000
BG_EVENT_USB_SPEED_UNKNOWN = 0x00008000
BG_EVENT_USB_LOW_SPEED = 0x00010000
BG_EVENT_USB_FULL_SPEED = 0x00020000
BG_EVENT_USB_HIGH_SPEED = 0x00040000
BG_EVENT_USB_LOW_OVER_FULL_SPEED = 0x00080000
BG_EVENT_USB_SUSPEND = 0x00100000
BG_EVENT_USB_RESUME = 0x00200000
BG_EVENT_USB_KEEP_ALIVE = 0x00400000
BG_EVENT_USB_DIGITAL_INPUT = 0x00800000
BG_EVENT_USB_OTG_HNP = 0x01000000
BG_EVENT_USB_OTG_SRP_DATA_PULSE = 0x02000000
BG_EVENT_USB_OTG_SRP_VBUS_PULSE = 0x04000000
# USB 5000 specific event codes
# USB 2.0
BG_EVENT_USB_SMA_EXTIN_DETECTED = 0x08000000
BG_EVENT_USB_CHIRP_DETECTED = 0x00000080
# USB 2.0 and USB 3.0 Trigger Event information
BG_EVENT_USB_VBUS_TRIGGER = 0x08000000
BG_EVENT_USB_COMPLEX_TIMER = 0x10000000
BG_EVENT_USB_CROSS_TRIGGER = 0x20000000
BG_EVENT_USB_COMPLEX_TRIGGER = 0x40000000
BG_EVENT_USB_TRIGGER = 0x80000000
BG_EVENT_USB_TRIGGER_STATE_MASK = 0x00000070
BG_EVENT_USB_TRIGGER_STATE_SHIFT = 4
BG_EVENT_USB_TRIGGER_STATE_0 = 0x00000000
BG_EVENT_USB_TRIGGER_STATE_1 = 0x00000010
BG_EVENT_USB_TRIGGER_STATE_2 = 0x00000020
BG_EVENT_USB_TRIGGER_STATE_3 = 0x00000030
BG_EVENT_USB_TRIGGER_STATE_4 = 0x00000040
BG_EVENT_USB_TRIGGER_STATE_5 = 0x00000050
BG_EVENT_USB_TRIGGER_STATE_6 = 0x00000060
BG_EVENT_USB_TRIGGER_STATE_7 = 0x00000070
# USB 3.0 US and DS, and ASYNC streams
BG_EVENT_USB_LFPS = 0x00001000
BG_EVENT_USB_LTSSM = 0x00002000
BG_EVENT_USB_VBUS_PRESENT = 0x00010000
BG_EVENT_USB_VBUS_ABSENT = 0x00020000
BG_EVENT_USB_SCRAMBLING_ENABLED = 0x00040000
BG_EVENT_USB_SCRAMBLING_DISABLED = 0x00080000
BG_EVENT_USB_POLARITY_NORMAL = 0x00100000
BG_EVENT_USB_POLARITY_REVERSED = 0x00200000
BG_EVENT_USB_PHY_ERROR = 0x00400000
BG_EVENT_USB_LTSSM_MASK = 0x000000ff
BG_EVENT_USB_LTSSM_STATE_UNKNOWN = 0x00000000
BG_EVENT_USB_LTSSM_STATE_SS_DISABLED = 0x00000001
BG_EVENT_USB_LTSSM_STATE_SS_INACTIVE = 0x00000002
BG_EVENT_USB_LTSSM_STATE_RX_DETECT_RESET = 0x00000003
BG_EVENT_USB_LTSSM_STATE_RX_DETECT_ACTIVE = 0x00000004
BG_EVENT_USB_LTSSM_STATE_POLLING_LFPS = 0x00000005
BG_EVENT_USB_LTSSM_STATE_POLLING_RXEQ = 0x00000006
BG_EVENT_USB_LTSSM_STATE_POLLING_ACTIVE = 0x00000007
BG_EVENT_USB_LTSSM_STATE_POLLING_CONFIG = 0x00000008
BG_EVENT_USB_LTSSM_STATE_POLLING_IDLE = 0x00000009
BG_EVENT_USB_LTSSM_STATE_U0 = 0x0000000a
BG_EVENT_USB_LTSSM_STATE_U1 = 0x0000000b
BG_EVENT_USB_LTSSM_STATE_U2 = 0x0000000c
BG_EVENT_USB_LTSSM_STATE_U3 = 0x0000000d
BG_EVENT_USB_LTSSM_STATE_RECOVERY_ACTIVE = 0x0000000e
BG_EVENT_USB_LTSSM_STATE_RECOVERY_CONFIG = 0x0000000f
BG_EVENT_USB_LTSSM_STATE_RECOVERY_IDLE = 0x00000010
BG_EVENT_USB_LTSSM_STATE_HOT_RESET_ACTIVE = 0x00000011
BG_EVENT_USB_LTSSM_STATE_HOT_RESET_EXIT = 0x00000012
BG_EVENT_USB_LTSSM_STATE_LOOPBACK_ACTIVE = 0x00000013
BG_EVENT_USB_LTSSM_STATE_LOOPBACK_EXIT = 0x00000014
BG_EVENT_USB_LTSSM_STATE_COMPLIANCE = 0x00000015
BG_EVENT_USB_SMA_EXTIN_ASSERTED = 0x01000000
BG_EVENT_USB_SMA_EXTIN_DEASSERTED = 0x02000000
BG_EVENT_USB_TRIGGER_5GBIT_START = 0x04000000
BG_EVENT_USB_TRIGGER_5GBIT_STOP = 0x08000000
# Beagle USB feature bits
BG_USB_FEATURE_NONE = 0x00000000
BG_USB_FEATURE_USB2_MON = 0x00000001
BG_USB_FEATURE_USB3_MON = 0x00000002
BG_USB_FEATURE_SIMUL_23 = 0x00000004
BG_USB_FEATURE_USB3_CMP_TRIG = 0x00000008
BG_USB_FEATURE_USB3_4G_MEM = 0x00000020
BG_USB_FEATURE_USB2_CMP_TRIG = 0x00000080
BG_USB_FEATURE_CROSS_ANALYZER_SYNC = 0x00000100
BG_USB_FEATURE_USB3_DOWNLINK = 0x00000200
BG_USB_FEATURE_IV_MON_LITE = 0x00000400
def bg_usb_features (beagle):
    """usage: int return = bg_usb_features(Beagle beagle)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_usb_features(beagle)


# License constants
BG_USB_LICENSE_LENGTH = 60
# Read the license key string and return the features
# Length must be set to BG_USB_LICENSE_LENGTH in order
# for license_key to be populated.
def bg_usb_license_read (beagle, license_key):
    """usage: (int return, u08[] license_key) = bg_usb_license_read(Beagle beagle, u08[] license_key)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function.

    Additionally, for arrays that are filled by the API function, an
    integer can be passed in place of the array argument and the API
    will automatically create an array of that length.  All output
    arrays, whether passed in or generated, are passed back in the
    returned tuple."""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # license_key pre-processing
    __license_key = isinstance(license_key, int)
    if __license_key:
        (license_key, length) = (array_u08(license_key), license_key)
    else:
        (license_key, length) = isinstance(license_key, ArrayType) and (license_key, len(license_key)) or (license_key[0], min(len(license_key[0]), int(license_key[1])))
        if license_key.typecode != 'B':
            raise TypeError("type for 'license_key' must be array('B')")
    # Call API function
    (_ret_) = api.py_bg_usb_license_read(beagle, length, license_key)
    # license_key post-processing
    if __license_key: del license_key[max(0, min(length, len(license_key))):]
    return (_ret_, license_key)


# Write the license key string and return the features
# Length must be set to BG_USB_LICENSE_LENGTH.  If
# the license is not valid or the length is not set to
# BG_USB_LICENSE_LENGTH, an invalid license error is
# returned.
def bg_usb_license_write (beagle, license_key):
    """usage: int return = bg_usb_license_write(Beagle beagle, u08[] license_key)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function."""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # license_key pre-processing
    (license_key, length) = isinstance(license_key, ArrayType) and (license_key, len(license_key)) or (license_key[0], min(len(license_key[0]), int(license_key[1])))
    if license_key.typecode != 'B':
        raise TypeError("type for 'license_key' must be array('B')")
    # Call API function
    return api.py_bg_usb_license_write(beagle, length, license_key)


# Capture modes
BG_USB_CAPTURE_USB3 = 0x01
BG_USB_CAPTURE_USB2 = 0x02
BG_USB_CAPTURE_IV_MON_LITE = 0x08
# Trigger modes
# enum BeagleUsbTriggerMode
BG_USB_TRIGGER_MODE_EVENT     = 0
BG_USB_TRIGGER_MODE_IMMEDIATE = 1

def bg_usb_configure (beagle, cap_mask, trigger_mode):
    """usage: int return = bg_usb_configure(Beagle beagle, u08 cap_mask, BeagleUsbTriggerMode trigger_mode)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_usb_configure(beagle, cap_mask, trigger_mode)


# USB Target Power
# enum BeagleUsbTargetPower
BG_USB_TARGET_POWER_HOST_SUPPLIED = 0
BG_USB_TARGET_POWER_OFF           = 1

def bg_usb_target_power (beagle, power_flag):
    """usage: int return = bg_usb_target_power(Beagle beagle, BeagleUsbTargetPower power_flag)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_usb_target_power(beagle, power_flag)


# USB 2 Configuration
# USB 2 Capture modes
# enum BeagleUsb2CaptureMode
BG_USB2_CAPTURE_REALTIME                 = 0
BG_USB2_CAPTURE_REALTIME_WITH_PROTECTION = 1
BG_USB2_CAPTURE_DELAYED_DOWNLOAD         = 2

def bg_usb2_capture_config (beagle, capture_mode):
    """usage: int return = bg_usb2_capture_config(Beagle beagle, BeagleUsb2CaptureMode capture_mode)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_usb2_capture_config(beagle, capture_mode)


# Target configs
BG_USB2_AUTO_SPEED_DETECT = 0
BG_USB2_LOW_SPEED = 1
BG_USB2_FULL_SPEED = 2
BG_USB2_HIGH_SPEED = 3
BG_USB2_VBUS_OVERRIDE = 0x00000080
def bg_usb2_target_config (beagle, target_config):
    """usage: int return = bg_usb2_target_config(Beagle beagle, u32 target_config)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_usb2_target_config(beagle, target_config)


# General constants
BG_USB_CAPTURE_SIZE_INFINITE = 0
BG_USB_CAPTURE_SIZE_SCALE = 0xffffffff
# USB 2 Capture modes
def bg_usb2_capture_buffer_config (beagle, pretrig_kb, capture_kb):
    """usage: int return = bg_usb2_capture_buffer_config(Beagle beagle, u32 pretrig_kb, u32 capture_kb)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_usb2_capture_buffer_config(beagle, pretrig_kb, capture_kb)


def bg_usb2_capture_buffer_config_query (beagle):
    """usage: (int return, u32 pretrig_kb, u32 capture_kb) = bg_usb2_capture_buffer_config_query(Beagle beagle)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_usb2_capture_buffer_config_query(beagle)


def bg_usb2_capture_status (beagle):
    """usage: (int return, BeagleCaptureStatus status, u32 pretrig_remaining_kb, u32 pretrig_total_kb, u32 capture_remaining_kb, u32 capture_total_kb) = bg_usb2_capture_status(Beagle beagle)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_usb2_capture_status(beagle)


# Digital output configuration
BG_USB2_DIGITAL_OUT_ENABLE_PIN1 = 0x01
BG_USB2_DIGITAL_OUT_PIN1_ACTIVE_HIGH = 0x01
BG_USB2_DIGITAL_OUT_PIN1_ACTIVE_LOW = 0x00
BG_USB2_DIGITAL_OUT_ENABLE_PIN2 = 0x02
BG_USB2_DIGITAL_OUT_PIN2_ACTIVE_HIGH = 0x02
BG_USB2_DIGITAL_OUT_PIN2_ACTIVE_LOW = 0x00
BG_USB2_DIGITAL_OUT_ENABLE_PIN3 = 0x04
BG_USB2_DIGITAL_OUT_PIN3_ACTIVE_HIGH = 0x04
BG_USB2_DIGITAL_OUT_PIN3_ACTIVE_LOW = 0x00
BG_USB2_DIGITAL_OUT_ENABLE_PIN4 = 0x08
BG_USB2_DIGITAL_OUT_PIN4_ACTIVE_HIGH = 0x08
BG_USB2_DIGITAL_OUT_PIN4_ACTIVE_LOW = 0x00
def bg_usb2_digital_out_config (beagle, out_enable_mask, out_polarity_mask):
    """usage: int return = bg_usb2_digital_out_config(Beagle beagle, u08 out_enable_mask, u08 out_polarity_mask)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_usb2_digital_out_config(beagle, out_enable_mask, out_polarity_mask)


# Digital output match pin configuration
# enum BeagleUsb2DigitalOutMatchPins
BG_USB2_DIGITAL_OUT_MATCH_PIN3 = 3
BG_USB2_DIGITAL_OUT_MATCH_PIN4 = 4

# Packet matching modes
# enum BeagleUsb2MatchType
BG_USB2_MATCH_TYPE_DISABLED  = 0
BG_USB2_MATCH_TYPE_EQUAL     = 1
BG_USB2_MATCH_TYPE_NOT_EQUAL = 2

# Digital ouput matching configuration
class BeagleUsb2PacketMatch:
    def __init__ (self):
        self.pid_match_type = 0
        self.pid_match_val  = 0
        self.dev_match_type = 0
        self.dev_match_val  = 0
        self.ep_match_type  = 0
        self.ep_match_val   = 0

# Data match PID mask
BG_USB2_DATA_MATCH_DATA0 = 0x01
BG_USB2_DATA_MATCH_DATA1 = 0x02
BG_USB2_DATA_MATCH_DATA2 = 0x04
BG_USB2_DATA_MATCH_MDATA = 0x08
class BeagleUsb2DataMatch:
    def __init__ (self):
        self.data_match_type   = 0
        self.data_match_pid    = 0
        self.data              = array('B')
        self.data_valid        = array('B')

def bg_usb2_digital_out_match (beagle, pin_num, packet_match, data_match):
    """usage: int return = bg_usb2_digital_out_match(Beagle beagle, BeagleUsb2DigitalOutMatchPins pin_num, BeagleUsb2PacketMatch packet_match, BeagleUsb2DataMatch data_match)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # packet_match pre-processing
    c_packet_match = None
    if packet_match != None:
        c_packet_match = (packet_match.pid_match_type, packet_match.pid_match_val, packet_match.dev_match_type, packet_match.dev_match_val, packet_match.ep_match_type, packet_match.ep_match_val)
    # data_match pre-processing
    c_data_match = None
    if data_match != None:
        c_data_match = (data_match.data_match_type, data_match.data_match_pid, data_match.data.buffer_info(), data_match.data_valid.buffer_info())
    # Call API function
    return api.py_bg_usb2_digital_out_match(beagle, pin_num, c_packet_match, c_data_match)


# Digital input pin configuration
BG_USB2_DIGITAL_IN_ENABLE_PIN1 = 0x01
BG_USB2_DIGITAL_IN_ENABLE_PIN2 = 0x02
BG_USB2_DIGITAL_IN_ENABLE_PIN3 = 0x04
BG_USB2_DIGITAL_IN_ENABLE_PIN4 = 0x08
def bg_usb2_digital_in_config (beagle, in_enable_mask):
    """usage: int return = bg_usb2_digital_in_config(Beagle beagle, u08 in_enable_mask)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_usb2_digital_in_config(beagle, in_enable_mask)


# Hardware filtering configuration
BG_USB2_HW_FILTER_PID_SOF = 0x01
BG_USB2_HW_FILTER_PID_IN = 0x02
BG_USB2_HW_FILTER_PID_PING = 0x04
BG_USB2_HW_FILTER_PID_PRE = 0x08
BG_USB2_HW_FILTER_PID_SPLIT = 0x10
BG_USB2_HW_FILTER_SELF = 0x20
def bg_usb2_hw_filter_config (beagle, filter_enable_mask):
    """usage: int return = bg_usb2_hw_filter_config(Beagle beagle, u08 filter_enable_mask)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_usb2_hw_filter_config(beagle, filter_enable_mask)


def bg_usb2_simple_match_config (beagle, dig_in_pin_pos_edge_mask, dig_in_pin_neg_edge_mask, dig_out_match_pin_mask):
    """usage: int return = bg_usb2_simple_match_config(Beagle beagle, u08 dig_in_pin_pos_edge_mask, u08 dig_in_pin_neg_edge_mask, u08 dig_out_match_pin_mask)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_usb2_simple_match_config(beagle, dig_in_pin_pos_edge_mask, dig_in_pin_neg_edge_mask, dig_out_match_pin_mask)


# USB 2.0 Complex matching enable/disable
def bg_usb2_complex_match_enable (beagle):
    """usage: int return = bg_usb2_complex_match_enable(Beagle beagle)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_usb2_complex_match_enable(beagle)


def bg_usb2_complex_match_disable (beagle):
    """usage: int return = bg_usb2_complex_match_disable(Beagle beagle)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_usb2_complex_match_disable(beagle)


# enum BeagleUsbMatchType
BG_USB_MATCH_TYPE_DISABLED      = 0
BG_USB_MATCH_TYPE_EQUAL         = 1
BG_USB_MATCH_TYPE_LESS_EQUAL    = 2
BG_USB_MATCH_TYPE_GREATER_EQUAL = 3
BG_USB_MATCH_TYPE_NOT_EQUAL     = 4

# enum BeagleUsb2DataMatchDirection
BG_USB2_MATCH_DIRECTION_DISABLED  = 0
BG_USB2_MATCH_DIRECTION_IN        = 1
BG_USB2_MATCH_DIRECTION_OUT_SETUP = 2
BG_USB2_MATCH_DIRECTION_SETUP     = 3

class BeagleUsb2DataProperties:
    def __init__ (self):
        self.direction           = 0
        self.ep_match_type       = 0
        self.ep_match_val        = 0
        self.dev_match_type      = 0
        self.dev_match_val       = 0
        self.data_len_match_type = 0
        self.data_len_match_val  = 0

# enum BeagleUsb2PacketType
BG_USB2_MATCH_PACKET_IN          = 0x0009
BG_USB2_MATCH_PACKET_OUT         = 0x0001
BG_USB2_MATCH_PACKET_SETUP       = 0x000d
BG_USB2_MATCH_PACKET_SOF         = 0x0005

BG_USB2_MATCH_PACKET_DATA0       = 0x0003
BG_USB2_MATCH_PACKET_DATA1       = 0x000b
BG_USB2_MATCH_PACKET_DATA2       = 0x0007
BG_USB2_MATCH_PACKET_MDATA       = 0x000f

BG_USB2_MATCH_PACKET_ACK         = 0x0002
BG_USB2_MATCH_PACKET_NAK         = 0x000a
BG_USB2_MATCH_PACKET_STALL       = 0x000e
BG_USB2_MATCH_PACKET_NYET        = 0x0006
BG_USB2_MATCH_PACKET_PRE         = 0x000c
BG_USB2_MATCH_PACKET_ERR         = 0x010c
BG_USB2_MATCH_PACKET_SPLIT       = 0x0008
BG_USB2_MATCH_PACKET_EXT         = 0x0000

BG_USB2_MATCH_PACKET_ANY         = 0x0010
BG_USB2_MATCH_PACKET_DATA0_DATA1 = 0x0020
BG_USB2_MATCH_PACKET_DATAX       = 0x0040
BG_USB2_MATCH_PACKET_SUBPID_MASK = 0x0100

BG_USB2_MATCH_PACKET_ERROR       = 0x1000

# enum BeagleUsb2DataMatchPrefix
BG_USB2_MATCH_PREFIX_DISABLED     = 0
BG_USB2_MATCH_PREFIX_IN           = 1
BG_USB2_MATCH_PREFIX_OUT          = 2
BG_USB2_MATCH_PREFIX_SETUP        = 3
BG_USB2_MATCH_PREFIX_CSPLIT       = 4
BG_USB2_MATCH_PREFIX_CSPLIT_IN    = 5
BG_USB2_MATCH_PREFIX_SSPLIT_OUT   = 6
BG_USB2_MATCH_PREFIX_SSPLIT_SETUP = 7

BG_USB2_MATCH_HANDSHAKE_MASK_DISABLED = 0x00000000
BG_USB2_MATCH_HANDSHAKE_MASK_NONE = 0x00000001
BG_USB2_MATCH_HANDSHAKE_MASK_ACK = 0x00000002
BG_USB2_MATCH_HANDSHAKE_MASK_NAK = 0x00000004
BG_USB2_MATCH_HANDSHAKE_MASK_NYET = 0x00000008
BG_USB2_MATCH_HANDSHAKE_MASK_STALL = 0x00000010
# enum BeagleUsb2ErrorType
BG_USB2_MATCH_CRC_DONT_CARE          =    0
BG_USB2_MATCH_CRC_VALID              =    1
BG_USB2_MATCH_CRC_INVALID            =    2
BG_USB2_MATCH_ERR_MASK_CORRUPTED_PID = 0x10
BG_USB2_MATCH_ERR_MASK_CRC           = 0x20
BG_USB2_MATCH_ERR_MASK_RXERROR       = 0x40
BG_USB2_MATCH_ERR_MASK_JABBER        = 0x80

# enum BeagleUsb2MatchModifier
BG_USB2_MATCH_MODIFIER_0 = 0
BG_USB2_MATCH_MODIFIER_1 = 1
BG_USB2_MATCH_MODIFIER_2 = 2
BG_USB2_MATCH_MODIFIER_3 = 3

BG_USB_COMPLEX_MATCH_ACTION_EXTOUT = 0x01
BG_USB_COMPLEX_MATCH_ACTION_TRIGGER = 0x02
BG_USB_COMPLEX_MATCH_ACTION_FILTER = 0x04
BG_USB_COMPLEX_MATCH_ACTION_GOTO = 0x08
class BeagleUsb2DataMatchUnit:
    def __init__ (self):
        self.packet_type           = 0
        self.prefix                = 0
        self.handshake             = 0
        self.data                  = array('B')
        self.data_valid            = array('B')
        self.err_match             = 0
        self.data_properties_valid = 0
        self.data_properties       = BeagleUsb2DataProperties()
        self.match_modifier        = 0
        self.repeat_count          = 0
        self.sticky_action         = 0
        self.action_mask           = 0
        self.goto_selector         = 0

# enum BeagleUsbTimerUnit
BG_USB_TIMER_UNIT_DISABLED = 0
BG_USB_TIMER_UNIT_NS       = 1
BG_USB_TIMER_UNIT_US       = 2
BG_USB_TIMER_UNIT_MS       = 3
BG_USB_TIMER_UNIT_SEC      = 4

class BeagleUsb2TimerMatchUnit:
    def __init__ (self):
        self.timer_unit    = 0
        self.timer_val     = 0
        self.action_mask   = 0
        self.goto_selector = 0

# enum BeagleUsb2AsyncEventType
BG_USB2_COMPLEX_MATCH_EVENT_DIGIN1        =  0
BG_USB2_COMPLEX_MATCH_EVENT_DIGIN2        =  1
BG_USB2_COMPLEX_MATCH_EVENT_DIGIN3        =  2
BG_USB2_COMPLEX_MATCH_EVENT_DIGIN4        =  3



BG_USB2_COMPLEX_MATCH_EVENT_CHIRP         = 13
BG_USB2_COMPLEX_MATCH_EVENT_SMA_EXTIN     = 14
BG_USB2_COMPLEX_MATCH_EVENT_CROSS_TRIGGER = 15
BG_USB2_COMPLEX_MATCH_EVENT_VBUS_TRIGGER  = 16

# enum BeagleUsb2VbusTriggerType
BG_USB2_VBUS_TRIGGER_TYPE_CURRENT = 1
BG_USB2_VBUS_TRIGGER_TYPE_VOLTAGE = 2

class BeagleUsb2AsyncEventMatchUnit:
    def __init__ (self):
        self.event_type        = 0
        self.edge_mask         = 0
        self.repeat_count      = 0
        self.sticky_action     = 0
        self.action_mask       = 0
        self.goto_selector     = 0
        self.vbus_trigger_type = 0
        self.vbus_trigger_val  = 0

class BeagleUsb2ComplexMatchState:
    def __init__ (self):
        self.data_0_valid = 0
        self.data_0       = BeagleUsb2DataMatchUnit()
        self.data_1_valid = 0
        self.data_1       = BeagleUsb2DataMatchUnit()
        self.data_2_valid = 0
        self.data_2       = BeagleUsb2DataMatchUnit()
        self.data_3_valid = 0
        self.data_3       = BeagleUsb2DataMatchUnit()
        self.timer_valid  = 0
        self.timer        = BeagleUsb2TimerMatchUnit()
        self.async_valid  = 0
        self.async        = BeagleUsb2AsyncEventMatchUnit()
        self.goto_0       = 0
        self.goto_1       = 0
        self.goto_2       = 0

def bg_usb2_complex_match_config (beagle, validate, digout, state_0, state_1, state_2, state_3, state_4, state_5, state_6, state_7):
    """usage: int return = bg_usb2_complex_match_config(Beagle beagle, u08 validate, u08 digout, BeagleUsb2ComplexMatchState state_0, BeagleUsb2ComplexMatchState state_1, BeagleUsb2ComplexMatchState state_2, BeagleUsb2ComplexMatchState state_3, BeagleUsb2ComplexMatchState state_4, BeagleUsb2ComplexMatchState state_5, BeagleUsb2ComplexMatchState state_6, BeagleUsb2ComplexMatchState state_7)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # state_0 pre-processing
    c_state_0 = None
    if state_0 != None:
        c_state_0 = (state_0.data_0_valid, state_0.data_0.packet_type, state_0.data_0.prefix, state_0.data_0.handshake, state_0.data_0.data.buffer_info(), state_0.data_0.data_valid.buffer_info(), state_0.data_0.err_match, state_0.data_0.data_properties_valid, state_0.data_0.data_properties.direction, state_0.data_0.data_properties.ep_match_type, state_0.data_0.data_properties.ep_match_val, state_0.data_0.data_properties.dev_match_type, state_0.data_0.data_properties.dev_match_val, state_0.data_0.data_properties.data_len_match_type, state_0.data_0.data_properties.data_len_match_val, state_0.data_0.match_modifier, state_0.data_0.repeat_count, state_0.data_0.sticky_action, state_0.data_0.action_mask, state_0.data_0.goto_selector, state_0.data_1_valid, state_0.data_1.packet_type, state_0.data_1.prefix, state_0.data_1.handshake, state_0.data_1.data.buffer_info(), state_0.data_1.data_valid.buffer_info(), state_0.data_1.err_match, state_0.data_1.data_properties_valid, state_0.data_1.data_properties.direction, state_0.data_1.data_properties.ep_match_type, state_0.data_1.data_properties.ep_match_val, state_0.data_1.data_properties.dev_match_type, state_0.data_1.data_properties.dev_match_val, state_0.data_1.data_properties.data_len_match_type, state_0.data_1.data_properties.data_len_match_val, state_0.data_1.match_modifier, state_0.data_1.repeat_count, state_0.data_1.sticky_action, state_0.data_1.action_mask, state_0.data_1.goto_selector, state_0.data_2_valid, state_0.data_2.packet_type, state_0.data_2.prefix, state_0.data_2.handshake, state_0.data_2.data.buffer_info(), state_0.data_2.data_valid.buffer_info(), state_0.data_2.err_match, state_0.data_2.data_properties_valid, state_0.data_2.data_properties.direction, state_0.data_2.data_properties.ep_match_type, state_0.data_2.data_properties.ep_match_val, state_0.data_2.data_properties.dev_match_type, state_0.data_2.data_properties.dev_match_val, state_0.data_2.data_properties.data_len_match_type, state_0.data_2.data_properties.data_len_match_val, state_0.data_2.match_modifier, state_0.data_2.repeat_count, state_0.data_2.sticky_action, state_0.data_2.action_mask, state_0.data_2.goto_selector, state_0.data_3_valid, state_0.data_3.packet_type, state_0.data_3.prefix, state_0.data_3.handshake, state_0.data_3.data.buffer_info(), state_0.data_3.data_valid.buffer_info(), state_0.data_3.err_match, state_0.data_3.data_properties_valid, state_0.data_3.data_properties.direction, state_0.data_3.data_properties.ep_match_type, state_0.data_3.data_properties.ep_match_val, state_0.data_3.data_properties.dev_match_type, state_0.data_3.data_properties.dev_match_val, state_0.data_3.data_properties.data_len_match_type, state_0.data_3.data_properties.data_len_match_val, state_0.data_3.match_modifier, state_0.data_3.repeat_count, state_0.data_3.sticky_action, state_0.data_3.action_mask, state_0.data_3.goto_selector, state_0.timer_valid, state_0.timer.timer_unit, state_0.timer.timer_val, state_0.timer.action_mask, state_0.timer.goto_selector, state_0.async_valid, state_0.async.event_type, state_0.async.edge_mask, state_0.async.repeat_count, state_0.async.sticky_action, state_0.async.action_mask, state_0.async.goto_selector, state_0.async.vbus_trigger_type, state_0.async.vbus_trigger_val, state_0.goto_0, state_0.goto_1, state_0.goto_2)
    # state_1 pre-processing
    c_state_1 = None
    if state_1 != None:
        c_state_1 = (state_1.data_0_valid, state_1.data_0.packet_type, state_1.data_0.prefix, state_1.data_0.handshake, state_1.data_0.data.buffer_info(), state_1.data_0.data_valid.buffer_info(), state_1.data_0.err_match, state_1.data_0.data_properties_valid, state_1.data_0.data_properties.direction, state_1.data_0.data_properties.ep_match_type, state_1.data_0.data_properties.ep_match_val, state_1.data_0.data_properties.dev_match_type, state_1.data_0.data_properties.dev_match_val, state_1.data_0.data_properties.data_len_match_type, state_1.data_0.data_properties.data_len_match_val, state_1.data_0.match_modifier, state_1.data_0.repeat_count, state_1.data_0.sticky_action, state_1.data_0.action_mask, state_1.data_0.goto_selector, state_1.data_1_valid, state_1.data_1.packet_type, state_1.data_1.prefix, state_1.data_1.handshake, state_1.data_1.data.buffer_info(), state_1.data_1.data_valid.buffer_info(), state_1.data_1.err_match, state_1.data_1.data_properties_valid, state_1.data_1.data_properties.direction, state_1.data_1.data_properties.ep_match_type, state_1.data_1.data_properties.ep_match_val, state_1.data_1.data_properties.dev_match_type, state_1.data_1.data_properties.dev_match_val, state_1.data_1.data_properties.data_len_match_type, state_1.data_1.data_properties.data_len_match_val, state_1.data_1.match_modifier, state_1.data_1.repeat_count, state_1.data_1.sticky_action, state_1.data_1.action_mask, state_1.data_1.goto_selector, state_1.data_2_valid, state_1.data_2.packet_type, state_1.data_2.prefix, state_1.data_2.handshake, state_1.data_2.data.buffer_info(), state_1.data_2.data_valid.buffer_info(), state_1.data_2.err_match, state_1.data_2.data_properties_valid, state_1.data_2.data_properties.direction, state_1.data_2.data_properties.ep_match_type, state_1.data_2.data_properties.ep_match_val, state_1.data_2.data_properties.dev_match_type, state_1.data_2.data_properties.dev_match_val, state_1.data_2.data_properties.data_len_match_type, state_1.data_2.data_properties.data_len_match_val, state_1.data_2.match_modifier, state_1.data_2.repeat_count, state_1.data_2.sticky_action, state_1.data_2.action_mask, state_1.data_2.goto_selector, state_1.data_3_valid, state_1.data_3.packet_type, state_1.data_3.prefix, state_1.data_3.handshake, state_1.data_3.data.buffer_info(), state_1.data_3.data_valid.buffer_info(), state_1.data_3.err_match, state_1.data_3.data_properties_valid, state_1.data_3.data_properties.direction, state_1.data_3.data_properties.ep_match_type, state_1.data_3.data_properties.ep_match_val, state_1.data_3.data_properties.dev_match_type, state_1.data_3.data_properties.dev_match_val, state_1.data_3.data_properties.data_len_match_type, state_1.data_3.data_properties.data_len_match_val, state_1.data_3.match_modifier, state_1.data_3.repeat_count, state_1.data_3.sticky_action, state_1.data_3.action_mask, state_1.data_3.goto_selector, state_1.timer_valid, state_1.timer.timer_unit, state_1.timer.timer_val, state_1.timer.action_mask, state_1.timer.goto_selector, state_1.async_valid, state_1.async.event_type, state_1.async.edge_mask, state_1.async.repeat_count, state_1.async.sticky_action, state_1.async.action_mask, state_1.async.goto_selector, state_1.async.vbus_trigger_type, state_1.async.vbus_trigger_val, state_1.goto_0, state_1.goto_1, state_1.goto_2)
    # state_2 pre-processing
    c_state_2 = None
    if state_2 != None:
        c_state_2 = (state_2.data_0_valid, state_2.data_0.packet_type, state_2.data_0.prefix, state_2.data_0.handshake, state_2.data_0.data.buffer_info(), state_2.data_0.data_valid.buffer_info(), state_2.data_0.err_match, state_2.data_0.data_properties_valid, state_2.data_0.data_properties.direction, state_2.data_0.data_properties.ep_match_type, state_2.data_0.data_properties.ep_match_val, state_2.data_0.data_properties.dev_match_type, state_2.data_0.data_properties.dev_match_val, state_2.data_0.data_properties.data_len_match_type, state_2.data_0.data_properties.data_len_match_val, state_2.data_0.match_modifier, state_2.data_0.repeat_count, state_2.data_0.sticky_action, state_2.data_0.action_mask, state_2.data_0.goto_selector, state_2.data_1_valid, state_2.data_1.packet_type, state_2.data_1.prefix, state_2.data_1.handshake, state_2.data_1.data.buffer_info(), state_2.data_1.data_valid.buffer_info(), state_2.data_1.err_match, state_2.data_1.data_properties_valid, state_2.data_1.data_properties.direction, state_2.data_1.data_properties.ep_match_type, state_2.data_1.data_properties.ep_match_val, state_2.data_1.data_properties.dev_match_type, state_2.data_1.data_properties.dev_match_val, state_2.data_1.data_properties.data_len_match_type, state_2.data_1.data_properties.data_len_match_val, state_2.data_1.match_modifier, state_2.data_1.repeat_count, state_2.data_1.sticky_action, state_2.data_1.action_mask, state_2.data_1.goto_selector, state_2.data_2_valid, state_2.data_2.packet_type, state_2.data_2.prefix, state_2.data_2.handshake, state_2.data_2.data.buffer_info(), state_2.data_2.data_valid.buffer_info(), state_2.data_2.err_match, state_2.data_2.data_properties_valid, state_2.data_2.data_properties.direction, state_2.data_2.data_properties.ep_match_type, state_2.data_2.data_properties.ep_match_val, state_2.data_2.data_properties.dev_match_type, state_2.data_2.data_properties.dev_match_val, state_2.data_2.data_properties.data_len_match_type, state_2.data_2.data_properties.data_len_match_val, state_2.data_2.match_modifier, state_2.data_2.repeat_count, state_2.data_2.sticky_action, state_2.data_2.action_mask, state_2.data_2.goto_selector, state_2.data_3_valid, state_2.data_3.packet_type, state_2.data_3.prefix, state_2.data_3.handshake, state_2.data_3.data.buffer_info(), state_2.data_3.data_valid.buffer_info(), state_2.data_3.err_match, state_2.data_3.data_properties_valid, state_2.data_3.data_properties.direction, state_2.data_3.data_properties.ep_match_type, state_2.data_3.data_properties.ep_match_val, state_2.data_3.data_properties.dev_match_type, state_2.data_3.data_properties.dev_match_val, state_2.data_3.data_properties.data_len_match_type, state_2.data_3.data_properties.data_len_match_val, state_2.data_3.match_modifier, state_2.data_3.repeat_count, state_2.data_3.sticky_action, state_2.data_3.action_mask, state_2.data_3.goto_selector, state_2.timer_valid, state_2.timer.timer_unit, state_2.timer.timer_val, state_2.timer.action_mask, state_2.timer.goto_selector, state_2.async_valid, state_2.async.event_type, state_2.async.edge_mask, state_2.async.repeat_count, state_2.async.sticky_action, state_2.async.action_mask, state_2.async.goto_selector, state_2.async.vbus_trigger_type, state_2.async.vbus_trigger_val, state_2.goto_0, state_2.goto_1, state_2.goto_2)
    # state_3 pre-processing
    c_state_3 = None
    if state_3 != None:
        c_state_3 = (state_3.data_0_valid, state_3.data_0.packet_type, state_3.data_0.prefix, state_3.data_0.handshake, state_3.data_0.data.buffer_info(), state_3.data_0.data_valid.buffer_info(), state_3.data_0.err_match, state_3.data_0.data_properties_valid, state_3.data_0.data_properties.direction, state_3.data_0.data_properties.ep_match_type, state_3.data_0.data_properties.ep_match_val, state_3.data_0.data_properties.dev_match_type, state_3.data_0.data_properties.dev_match_val, state_3.data_0.data_properties.data_len_match_type, state_3.data_0.data_properties.data_len_match_val, state_3.data_0.match_modifier, state_3.data_0.repeat_count, state_3.data_0.sticky_action, state_3.data_0.action_mask, state_3.data_0.goto_selector, state_3.data_1_valid, state_3.data_1.packet_type, state_3.data_1.prefix, state_3.data_1.handshake, state_3.data_1.data.buffer_info(), state_3.data_1.data_valid.buffer_info(), state_3.data_1.err_match, state_3.data_1.data_properties_valid, state_3.data_1.data_properties.direction, state_3.data_1.data_properties.ep_match_type, state_3.data_1.data_properties.ep_match_val, state_3.data_1.data_properties.dev_match_type, state_3.data_1.data_properties.dev_match_val, state_3.data_1.data_properties.data_len_match_type, state_3.data_1.data_properties.data_len_match_val, state_3.data_1.match_modifier, state_3.data_1.repeat_count, state_3.data_1.sticky_action, state_3.data_1.action_mask, state_3.data_1.goto_selector, state_3.data_2_valid, state_3.data_2.packet_type, state_3.data_2.prefix, state_3.data_2.handshake, state_3.data_2.data.buffer_info(), state_3.data_2.data_valid.buffer_info(), state_3.data_2.err_match, state_3.data_2.data_properties_valid, state_3.data_2.data_properties.direction, state_3.data_2.data_properties.ep_match_type, state_3.data_2.data_properties.ep_match_val, state_3.data_2.data_properties.dev_match_type, state_3.data_2.data_properties.dev_match_val, state_3.data_2.data_properties.data_len_match_type, state_3.data_2.data_properties.data_len_match_val, state_3.data_2.match_modifier, state_3.data_2.repeat_count, state_3.data_2.sticky_action, state_3.data_2.action_mask, state_3.data_2.goto_selector, state_3.data_3_valid, state_3.data_3.packet_type, state_3.data_3.prefix, state_3.data_3.handshake, state_3.data_3.data.buffer_info(), state_3.data_3.data_valid.buffer_info(), state_3.data_3.err_match, state_3.data_3.data_properties_valid, state_3.data_3.data_properties.direction, state_3.data_3.data_properties.ep_match_type, state_3.data_3.data_properties.ep_match_val, state_3.data_3.data_properties.dev_match_type, state_3.data_3.data_properties.dev_match_val, state_3.data_3.data_properties.data_len_match_type, state_3.data_3.data_properties.data_len_match_val, state_3.data_3.match_modifier, state_3.data_3.repeat_count, state_3.data_3.sticky_action, state_3.data_3.action_mask, state_3.data_3.goto_selector, state_3.timer_valid, state_3.timer.timer_unit, state_3.timer.timer_val, state_3.timer.action_mask, state_3.timer.goto_selector, state_3.async_valid, state_3.async.event_type, state_3.async.edge_mask, state_3.async.repeat_count, state_3.async.sticky_action, state_3.async.action_mask, state_3.async.goto_selector, state_3.async.vbus_trigger_type, state_3.async.vbus_trigger_val, state_3.goto_0, state_3.goto_1, state_3.goto_2)
    # state_4 pre-processing
    c_state_4 = None
    if state_4 != None:
        c_state_4 = (state_4.data_0_valid, state_4.data_0.packet_type, state_4.data_0.prefix, state_4.data_0.handshake, state_4.data_0.data.buffer_info(), state_4.data_0.data_valid.buffer_info(), state_4.data_0.err_match, state_4.data_0.data_properties_valid, state_4.data_0.data_properties.direction, state_4.data_0.data_properties.ep_match_type, state_4.data_0.data_properties.ep_match_val, state_4.data_0.data_properties.dev_match_type, state_4.data_0.data_properties.dev_match_val, state_4.data_0.data_properties.data_len_match_type, state_4.data_0.data_properties.data_len_match_val, state_4.data_0.match_modifier, state_4.data_0.repeat_count, state_4.data_0.sticky_action, state_4.data_0.action_mask, state_4.data_0.goto_selector, state_4.data_1_valid, state_4.data_1.packet_type, state_4.data_1.prefix, state_4.data_1.handshake, state_4.data_1.data.buffer_info(), state_4.data_1.data_valid.buffer_info(), state_4.data_1.err_match, state_4.data_1.data_properties_valid, state_4.data_1.data_properties.direction, state_4.data_1.data_properties.ep_match_type, state_4.data_1.data_properties.ep_match_val, state_4.data_1.data_properties.dev_match_type, state_4.data_1.data_properties.dev_match_val, state_4.data_1.data_properties.data_len_match_type, state_4.data_1.data_properties.data_len_match_val, state_4.data_1.match_modifier, state_4.data_1.repeat_count, state_4.data_1.sticky_action, state_4.data_1.action_mask, state_4.data_1.goto_selector, state_4.data_2_valid, state_4.data_2.packet_type, state_4.data_2.prefix, state_4.data_2.handshake, state_4.data_2.data.buffer_info(), state_4.data_2.data_valid.buffer_info(), state_4.data_2.err_match, state_4.data_2.data_properties_valid, state_4.data_2.data_properties.direction, state_4.data_2.data_properties.ep_match_type, state_4.data_2.data_properties.ep_match_val, state_4.data_2.data_properties.dev_match_type, state_4.data_2.data_properties.dev_match_val, state_4.data_2.data_properties.data_len_match_type, state_4.data_2.data_properties.data_len_match_val, state_4.data_2.match_modifier, state_4.data_2.repeat_count, state_4.data_2.sticky_action, state_4.data_2.action_mask, state_4.data_2.goto_selector, state_4.data_3_valid, state_4.data_3.packet_type, state_4.data_3.prefix, state_4.data_3.handshake, state_4.data_3.data.buffer_info(), state_4.data_3.data_valid.buffer_info(), state_4.data_3.err_match, state_4.data_3.data_properties_valid, state_4.data_3.data_properties.direction, state_4.data_3.data_properties.ep_match_type, state_4.data_3.data_properties.ep_match_val, state_4.data_3.data_properties.dev_match_type, state_4.data_3.data_properties.dev_match_val, state_4.data_3.data_properties.data_len_match_type, state_4.data_3.data_properties.data_len_match_val, state_4.data_3.match_modifier, state_4.data_3.repeat_count, state_4.data_3.sticky_action, state_4.data_3.action_mask, state_4.data_3.goto_selector, state_4.timer_valid, state_4.timer.timer_unit, state_4.timer.timer_val, state_4.timer.action_mask, state_4.timer.goto_selector, state_4.async_valid, state_4.async.event_type, state_4.async.edge_mask, state_4.async.repeat_count, state_4.async.sticky_action, state_4.async.action_mask, state_4.async.goto_selector, state_4.async.vbus_trigger_type, state_4.async.vbus_trigger_val, state_4.goto_0, state_4.goto_1, state_4.goto_2)
    # state_5 pre-processing
    c_state_5 = None
    if state_5 != None:
        c_state_5 = (state_5.data_0_valid, state_5.data_0.packet_type, state_5.data_0.prefix, state_5.data_0.handshake, state_5.data_0.data.buffer_info(), state_5.data_0.data_valid.buffer_info(), state_5.data_0.err_match, state_5.data_0.data_properties_valid, state_5.data_0.data_properties.direction, state_5.data_0.data_properties.ep_match_type, state_5.data_0.data_properties.ep_match_val, state_5.data_0.data_properties.dev_match_type, state_5.data_0.data_properties.dev_match_val, state_5.data_0.data_properties.data_len_match_type, state_5.data_0.data_properties.data_len_match_val, state_5.data_0.match_modifier, state_5.data_0.repeat_count, state_5.data_0.sticky_action, state_5.data_0.action_mask, state_5.data_0.goto_selector, state_5.data_1_valid, state_5.data_1.packet_type, state_5.data_1.prefix, state_5.data_1.handshake, state_5.data_1.data.buffer_info(), state_5.data_1.data_valid.buffer_info(), state_5.data_1.err_match, state_5.data_1.data_properties_valid, state_5.data_1.data_properties.direction, state_5.data_1.data_properties.ep_match_type, state_5.data_1.data_properties.ep_match_val, state_5.data_1.data_properties.dev_match_type, state_5.data_1.data_properties.dev_match_val, state_5.data_1.data_properties.data_len_match_type, state_5.data_1.data_properties.data_len_match_val, state_5.data_1.match_modifier, state_5.data_1.repeat_count, state_5.data_1.sticky_action, state_5.data_1.action_mask, state_5.data_1.goto_selector, state_5.data_2_valid, state_5.data_2.packet_type, state_5.data_2.prefix, state_5.data_2.handshake, state_5.data_2.data.buffer_info(), state_5.data_2.data_valid.buffer_info(), state_5.data_2.err_match, state_5.data_2.data_properties_valid, state_5.data_2.data_properties.direction, state_5.data_2.data_properties.ep_match_type, state_5.data_2.data_properties.ep_match_val, state_5.data_2.data_properties.dev_match_type, state_5.data_2.data_properties.dev_match_val, state_5.data_2.data_properties.data_len_match_type, state_5.data_2.data_properties.data_len_match_val, state_5.data_2.match_modifier, state_5.data_2.repeat_count, state_5.data_2.sticky_action, state_5.data_2.action_mask, state_5.data_2.goto_selector, state_5.data_3_valid, state_5.data_3.packet_type, state_5.data_3.prefix, state_5.data_3.handshake, state_5.data_3.data.buffer_info(), state_5.data_3.data_valid.buffer_info(), state_5.data_3.err_match, state_5.data_3.data_properties_valid, state_5.data_3.data_properties.direction, state_5.data_3.data_properties.ep_match_type, state_5.data_3.data_properties.ep_match_val, state_5.data_3.data_properties.dev_match_type, state_5.data_3.data_properties.dev_match_val, state_5.data_3.data_properties.data_len_match_type, state_5.data_3.data_properties.data_len_match_val, state_5.data_3.match_modifier, state_5.data_3.repeat_count, state_5.data_3.sticky_action, state_5.data_3.action_mask, state_5.data_3.goto_selector, state_5.timer_valid, state_5.timer.timer_unit, state_5.timer.timer_val, state_5.timer.action_mask, state_5.timer.goto_selector, state_5.async_valid, state_5.async.event_type, state_5.async.edge_mask, state_5.async.repeat_count, state_5.async.sticky_action, state_5.async.action_mask, state_5.async.goto_selector, state_5.async.vbus_trigger_type, state_5.async.vbus_trigger_val, state_5.goto_0, state_5.goto_1, state_5.goto_2)
    # state_6 pre-processing
    c_state_6 = None
    if state_6 != None:
        c_state_6 = (state_6.data_0_valid, state_6.data_0.packet_type, state_6.data_0.prefix, state_6.data_0.handshake, state_6.data_0.data.buffer_info(), state_6.data_0.data_valid.buffer_info(), state_6.data_0.err_match, state_6.data_0.data_properties_valid, state_6.data_0.data_properties.direction, state_6.data_0.data_properties.ep_match_type, state_6.data_0.data_properties.ep_match_val, state_6.data_0.data_properties.dev_match_type, state_6.data_0.data_properties.dev_match_val, state_6.data_0.data_properties.data_len_match_type, state_6.data_0.data_properties.data_len_match_val, state_6.data_0.match_modifier, state_6.data_0.repeat_count, state_6.data_0.sticky_action, state_6.data_0.action_mask, state_6.data_0.goto_selector, state_6.data_1_valid, state_6.data_1.packet_type, state_6.data_1.prefix, state_6.data_1.handshake, state_6.data_1.data.buffer_info(), state_6.data_1.data_valid.buffer_info(), state_6.data_1.err_match, state_6.data_1.data_properties_valid, state_6.data_1.data_properties.direction, state_6.data_1.data_properties.ep_match_type, state_6.data_1.data_properties.ep_match_val, state_6.data_1.data_properties.dev_match_type, state_6.data_1.data_properties.dev_match_val, state_6.data_1.data_properties.data_len_match_type, state_6.data_1.data_properties.data_len_match_val, state_6.data_1.match_modifier, state_6.data_1.repeat_count, state_6.data_1.sticky_action, state_6.data_1.action_mask, state_6.data_1.goto_selector, state_6.data_2_valid, state_6.data_2.packet_type, state_6.data_2.prefix, state_6.data_2.handshake, state_6.data_2.data.buffer_info(), state_6.data_2.data_valid.buffer_info(), state_6.data_2.err_match, state_6.data_2.data_properties_valid, state_6.data_2.data_properties.direction, state_6.data_2.data_properties.ep_match_type, state_6.data_2.data_properties.ep_match_val, state_6.data_2.data_properties.dev_match_type, state_6.data_2.data_properties.dev_match_val, state_6.data_2.data_properties.data_len_match_type, state_6.data_2.data_properties.data_len_match_val, state_6.data_2.match_modifier, state_6.data_2.repeat_count, state_6.data_2.sticky_action, state_6.data_2.action_mask, state_6.data_2.goto_selector, state_6.data_3_valid, state_6.data_3.packet_type, state_6.data_3.prefix, state_6.data_3.handshake, state_6.data_3.data.buffer_info(), state_6.data_3.data_valid.buffer_info(), state_6.data_3.err_match, state_6.data_3.data_properties_valid, state_6.data_3.data_properties.direction, state_6.data_3.data_properties.ep_match_type, state_6.data_3.data_properties.ep_match_val, state_6.data_3.data_properties.dev_match_type, state_6.data_3.data_properties.dev_match_val, state_6.data_3.data_properties.data_len_match_type, state_6.data_3.data_properties.data_len_match_val, state_6.data_3.match_modifier, state_6.data_3.repeat_count, state_6.data_3.sticky_action, state_6.data_3.action_mask, state_6.data_3.goto_selector, state_6.timer_valid, state_6.timer.timer_unit, state_6.timer.timer_val, state_6.timer.action_mask, state_6.timer.goto_selector, state_6.async_valid, state_6.async.event_type, state_6.async.edge_mask, state_6.async.repeat_count, state_6.async.sticky_action, state_6.async.action_mask, state_6.async.goto_selector, state_6.async.vbus_trigger_type, state_6.async.vbus_trigger_val, state_6.goto_0, state_6.goto_1, state_6.goto_2)
    # state_7 pre-processing
    c_state_7 = None
    if state_7 != None:
        c_state_7 = (state_7.data_0_valid, state_7.data_0.packet_type, state_7.data_0.prefix, state_7.data_0.handshake, state_7.data_0.data.buffer_info(), state_7.data_0.data_valid.buffer_info(), state_7.data_0.err_match, state_7.data_0.data_properties_valid, state_7.data_0.data_properties.direction, state_7.data_0.data_properties.ep_match_type, state_7.data_0.data_properties.ep_match_val, state_7.data_0.data_properties.dev_match_type, state_7.data_0.data_properties.dev_match_val, state_7.data_0.data_properties.data_len_match_type, state_7.data_0.data_properties.data_len_match_val, state_7.data_0.match_modifier, state_7.data_0.repeat_count, state_7.data_0.sticky_action, state_7.data_0.action_mask, state_7.data_0.goto_selector, state_7.data_1_valid, state_7.data_1.packet_type, state_7.data_1.prefix, state_7.data_1.handshake, state_7.data_1.data.buffer_info(), state_7.data_1.data_valid.buffer_info(), state_7.data_1.err_match, state_7.data_1.data_properties_valid, state_7.data_1.data_properties.direction, state_7.data_1.data_properties.ep_match_type, state_7.data_1.data_properties.ep_match_val, state_7.data_1.data_properties.dev_match_type, state_7.data_1.data_properties.dev_match_val, state_7.data_1.data_properties.data_len_match_type, state_7.data_1.data_properties.data_len_match_val, state_7.data_1.match_modifier, state_7.data_1.repeat_count, state_7.data_1.sticky_action, state_7.data_1.action_mask, state_7.data_1.goto_selector, state_7.data_2_valid, state_7.data_2.packet_type, state_7.data_2.prefix, state_7.data_2.handshake, state_7.data_2.data.buffer_info(), state_7.data_2.data_valid.buffer_info(), state_7.data_2.err_match, state_7.data_2.data_properties_valid, state_7.data_2.data_properties.direction, state_7.data_2.data_properties.ep_match_type, state_7.data_2.data_properties.ep_match_val, state_7.data_2.data_properties.dev_match_type, state_7.data_2.data_properties.dev_match_val, state_7.data_2.data_properties.data_len_match_type, state_7.data_2.data_properties.data_len_match_val, state_7.data_2.match_modifier, state_7.data_2.repeat_count, state_7.data_2.sticky_action, state_7.data_2.action_mask, state_7.data_2.goto_selector, state_7.data_3_valid, state_7.data_3.packet_type, state_7.data_3.prefix, state_7.data_3.handshake, state_7.data_3.data.buffer_info(), state_7.data_3.data_valid.buffer_info(), state_7.data_3.err_match, state_7.data_3.data_properties_valid, state_7.data_3.data_properties.direction, state_7.data_3.data_properties.ep_match_type, state_7.data_3.data_properties.ep_match_val, state_7.data_3.data_properties.dev_match_type, state_7.data_3.data_properties.dev_match_val, state_7.data_3.data_properties.data_len_match_type, state_7.data_3.data_properties.data_len_match_val, state_7.data_3.match_modifier, state_7.data_3.repeat_count, state_7.data_3.sticky_action, state_7.data_3.action_mask, state_7.data_3.goto_selector, state_7.timer_valid, state_7.timer.timer_unit, state_7.timer.timer_val, state_7.timer.action_mask, state_7.timer.goto_selector, state_7.async_valid, state_7.async.event_type, state_7.async.edge_mask, state_7.async.repeat_count, state_7.async.sticky_action, state_7.async.action_mask, state_7.async.goto_selector, state_7.async.vbus_trigger_type, state_7.async.vbus_trigger_val, state_7.goto_0, state_7.goto_1, state_7.goto_2)
    # Call API function
    return api.py_bg_usb2_complex_match_config(beagle, validate, digout, c_state_0, c_state_1, c_state_2, c_state_3, c_state_4, c_state_5, c_state_6, c_state_7)


def bg_usb2_complex_match_config_single (beagle, validate, digout, state):
    """usage: int return = bg_usb2_complex_match_config_single(Beagle beagle, u08 validate, u08 digout, BeagleUsb2ComplexMatchState state)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # state pre-processing
    c_state = None
    if state != None:
        c_state = (state.data_0_valid, state.data_0.packet_type, state.data_0.prefix, state.data_0.handshake, state.data_0.data.buffer_info(), state.data_0.data_valid.buffer_info(), state.data_0.err_match, state.data_0.data_properties_valid, state.data_0.data_properties.direction, state.data_0.data_properties.ep_match_type, state.data_0.data_properties.ep_match_val, state.data_0.data_properties.dev_match_type, state.data_0.data_properties.dev_match_val, state.data_0.data_properties.data_len_match_type, state.data_0.data_properties.data_len_match_val, state.data_0.match_modifier, state.data_0.repeat_count, state.data_0.sticky_action, state.data_0.action_mask, state.data_0.goto_selector, state.data_1_valid, state.data_1.packet_type, state.data_1.prefix, state.data_1.handshake, state.data_1.data.buffer_info(), state.data_1.data_valid.buffer_info(), state.data_1.err_match, state.data_1.data_properties_valid, state.data_1.data_properties.direction, state.data_1.data_properties.ep_match_type, state.data_1.data_properties.ep_match_val, state.data_1.data_properties.dev_match_type, state.data_1.data_properties.dev_match_val, state.data_1.data_properties.data_len_match_type, state.data_1.data_properties.data_len_match_val, state.data_1.match_modifier, state.data_1.repeat_count, state.data_1.sticky_action, state.data_1.action_mask, state.data_1.goto_selector, state.data_2_valid, state.data_2.packet_type, state.data_2.prefix, state.data_2.handshake, state.data_2.data.buffer_info(), state.data_2.data_valid.buffer_info(), state.data_2.err_match, state.data_2.data_properties_valid, state.data_2.data_properties.direction, state.data_2.data_properties.ep_match_type, state.data_2.data_properties.ep_match_val, state.data_2.data_properties.dev_match_type, state.data_2.data_properties.dev_match_val, state.data_2.data_properties.data_len_match_type, state.data_2.data_properties.data_len_match_val, state.data_2.match_modifier, state.data_2.repeat_count, state.data_2.sticky_action, state.data_2.action_mask, state.data_2.goto_selector, state.data_3_valid, state.data_3.packet_type, state.data_3.prefix, state.data_3.handshake, state.data_3.data.buffer_info(), state.data_3.data_valid.buffer_info(), state.data_3.err_match, state.data_3.data_properties_valid, state.data_3.data_properties.direction, state.data_3.data_properties.ep_match_type, state.data_3.data_properties.ep_match_val, state.data_3.data_properties.dev_match_type, state.data_3.data_properties.dev_match_val, state.data_3.data_properties.data_len_match_type, state.data_3.data_properties.data_len_match_val, state.data_3.match_modifier, state.data_3.repeat_count, state.data_3.sticky_action, state.data_3.action_mask, state.data_3.goto_selector, state.timer_valid, state.timer.timer_unit, state.timer.timer_val, state.timer.action_mask, state.timer.goto_selector, state.async_valid, state.async.event_type, state.async.edge_mask, state.async.repeat_count, state.async.sticky_action, state.async.action_mask, state.async.goto_selector, state.async.vbus_trigger_type, state.async.vbus_trigger_val, state.goto_0, state.goto_1, state.goto_2)
    # Call API function
    return api.py_bg_usb2_complex_match_config_single(beagle, validate, digout, c_state)


# enum BeagleUsbExtoutType
BG_USB_EXTOUT_LOW       = 0
BG_USB_EXTOUT_HIGH      = 1
BG_USB_EXTOUT_POS_PULSE = 2
BG_USB_EXTOUT_NEG_PULSE = 3
BG_USB_EXTOUT_TOGGLE_0  = 4
BG_USB_EXTOUT_TOGGLE_1  = 5

def bg_usb2_extout_config (beagle, extout_modulation):
    """usage: int return = bg_usb2_extout_config(Beagle beagle, BeagleUsbExtoutType extout_modulation)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_usb2_extout_config(beagle, extout_modulation)


# enum BeagleMemoryTestResult
BG_USB_MEMORY_TEST_PASS = 0
BG_USB_MEMORY_TEST_FAIL = 1

def bg_usb2_memory_test (beagle):
    """usage: int return = bg_usb2_memory_test(Beagle beagle)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_usb2_memory_test(beagle)


# USB 3 Configuration
# USB 3 Capture modes
def bg_usb3_capture_buffer_config (beagle, pretrig_kb, capture_kb):
    """usage: int return = bg_usb3_capture_buffer_config(Beagle beagle, u32 pretrig_kb, u32 capture_kb)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_usb3_capture_buffer_config(beagle, pretrig_kb, capture_kb)


def bg_usb3_capture_buffer_config_query (beagle):
    """usage: (int return, u32 pretrig_kb, u32 capture_kb) = bg_usb3_capture_buffer_config_query(Beagle beagle)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_usb3_capture_buffer_config_query(beagle)


def bg_usb3_capture_status (beagle):
    """usage: (int return, BeagleCaptureStatus status, u32 pretrig_remaining_kb, u32 pretrig_total_kb, u32 capture_remaining_kb, u32 capture_total_kb) = bg_usb3_capture_status(Beagle beagle)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_usb3_capture_status(beagle)


BG_USB3_PHY_CONFIG_POLARITY_NON_INVERT = 0x00
BG_USB3_PHY_CONFIG_POLARITY_INVERT = 0x01
BG_USB3_PHY_CONFIG_POLARITY_AUTO = 0x02
BG_USB3_PHY_CONFIG_POLARITY_MASK = 0x03
BG_USB3_PHY_CONFIG_DESCRAMBLER_ON = 0x00
BG_USB3_PHY_CONFIG_DESCRAMBLER_OFF = 0x04
BG_USB3_PHY_CONFIG_DESCRAMBLER_AUTO = 0x08
BG_USB3_PHY_CONFIG_DESCRAMBLER_MASK = 0x0c
BG_USB3_PHY_CONFIG_RXTERM_ON = 0x00
BG_USB3_PHY_CONFIG_RXTERM_OFF = 0x10
BG_USB3_PHY_CONFIG_RXTERM_AUTO = 0x20
BG_USB3_PHY_CONFIG_RXTERM_MASK = 0x30
def bg_usb3_phy_config (beagle, tx, rx):
    """usage: int return = bg_usb3_phy_config(Beagle beagle, u08 tx, u08 rx)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_usb3_phy_config(beagle, tx, rx)


BG_USB3_TRUNCATION_OFF = 0x00
BG_USB3_TRUNCATION_20 = 0x01
BG_USB3_TRUNCATION_36 = 0x02
BG_USB3_TRUNCATION_68 = 0x03
def bg_usb3_truncation_mode (beagle, tx_truncation_mode, rx_truncation_mode):
    """usage: int return = bg_usb3_truncation_mode(Beagle beagle, u08 tx_truncation_mode, u08 rx_truncation_mode)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_usb3_truncation_mode(beagle, tx_truncation_mode, rx_truncation_mode)


# Channel Configuration
BG_USB3_EQUALIZATION_OFF = 0
BG_USB3_EQUALIZATION_MIN = 1
BG_USB3_EQUALIZATION_MOD = 2
BG_USB3_EQUALIZATION_MAX = 3
class BeagleUsb3Channel:
    def __init__ (self):
        self.input_equalization_short  = 0
        self.input_equalization_medium = 0
        self.input_equalization_long   = 0
        self.pre_emphasis_short_level  = 0
        self.pre_emphasis_short_decay  = 0
        self.pre_emphasis_long_level   = 0
        self.pre_emphasis_long_decay   = 0
        self.output_level              = 0

def bg_usb3_link_config (beagle, tx, rx):
    """usage: int return = bg_usb3_link_config(Beagle beagle, BeagleUsb3Channel tx, BeagleUsb3Channel rx)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # tx pre-processing
    c_tx = None
    if tx != None:
        c_tx = (tx.input_equalization_short, tx.input_equalization_medium, tx.input_equalization_long, tx.pre_emphasis_short_level, tx.pre_emphasis_short_decay, tx.pre_emphasis_long_level, tx.pre_emphasis_long_decay, tx.output_level)
    # rx pre-processing
    c_rx = None
    if rx != None:
        c_rx = (rx.input_equalization_short, rx.input_equalization_medium, rx.input_equalization_long, rx.pre_emphasis_short_level, rx.pre_emphasis_short_decay, rx.pre_emphasis_long_level, rx.pre_emphasis_long_decay, rx.output_level)
    # Call API function
    return api.py_bg_usb3_link_config(beagle, c_tx, c_rx)


# Simple match configuration
BG_USB3_SIMPLE_MATCH_NONE = 0x00000000
BG_USB3_SIMPLE_MATCH_SSTX_IPS = 0x00000001
BG_USB3_SIMPLE_MATCH_SSTX_SLC = 0x00000002
BG_USB3_SIMPLE_MATCH_SSTX_SHP = 0x00000004
BG_USB3_SIMPLE_MATCH_SSTX_SDP = 0x00000008
BG_USB3_SIMPLE_MATCH_SSRX_IPS = 0x00000010
BG_USB3_SIMPLE_MATCH_SSRX_SLC = 0x00000020
BG_USB3_SIMPLE_MATCH_SSRX_SHP = 0x00000040
BG_USB3_SIMPLE_MATCH_SSRX_SDP = 0x00000080
BG_USB3_SIMPLE_MATCH_SSTX_SLC_CRC_5A_CRC_5B = 0x00000100
BG_USB3_SIMPLE_MATCH_SSTX_SHP_CRC_5 = 0x00000200
BG_USB3_SIMPLE_MATCH_SSTX_SHP_CRC_16 = 0x00000400
BG_USB3_SIMPLE_MATCH_SSTX_SDP_CRC = 0x00000800
BG_USB3_SIMPLE_MATCH_SSRX_SLC_CRC_5A_CRC_5B = 0x00001000
BG_USB3_SIMPLE_MATCH_SSRX_SHP_CRC_5 = 0x00002000
BG_USB3_SIMPLE_MATCH_SSRX_SHP_CRC_16 = 0x00004000
BG_USB3_SIMPLE_MATCH_SSRX_SDP_CRC = 0x00008000
BG_USB3_SIMPLE_MATCH_EVENT_SSTX_LFPS = 0x00010000
BG_USB3_SIMPLE_MATCH_EVENT_SSTX_POLARITY = 0x00020000
BG_USB3_SIMPLE_MATCH_EVENT_SSTX_DETECTED = 0x00400000
BG_USB3_SIMPLE_MATCH_EVENT_SSTX_SCRAMBLE = 0x00080000
BG_USB3_SIMPLE_MATCH_EVENT_SSRX_LFPS = 0x00100000
BG_USB3_SIMPLE_MATCH_EVENT_SSRX_POLARITY = 0x00200000
BG_USB3_SIMPLE_MATCH_EVENT_SSRX_DETECTED = 0x00040000
BG_USB3_SIMPLE_MATCH_EVENT_SSRX_SCRAMBLE = 0x00800000
BG_USB3_SIMPLE_MATCH_EVENT_VBUS_PRESENT = 0x08000000
BG_USB3_SIMPLE_MATCH_EVENT_SSTX_PHYERR = 0x10000000
BG_USB3_SIMPLE_MATCH_EVENT_SSRX_PHYERR = 0x20000000
BG_USB3_SIMPLE_MATCH_EVENT_SMA_EXTIN = 0x40000000
BG_USB_EDGE_RISING = 0x01
BG_USB_EDGE_PULSE = 0x01
BG_USB_EDGE_FALLING = 0x02
BG_USB_EDGE_DEVICE_CHIRP = 0x01
BG_USB_EDGE_HOST_CHIRP = 0x02
# enum BeagleUsb3ExtoutMode
BG_USB3_EXTOUT_DISABLED     = 0
BG_USB3_EXTOUT_TRIGGER_MODE = 1
BG_USB3_EXTOUT_EVENTS_MODE  = 2

# enum BeagleUsb3IPSType
BG_USB3_IPS_TYPE_DISABLED = 0
BG_USB3_IPS_TYPE_TS1      = 1
BG_USB3_IPS_TYPE_TS2      = 2
BG_USB3_IPS_TYPE_TSEQ     = 3
BG_USB3_IPS_TYPE_TSx      = 4
BG_USB3_IPS_TYPE_TS_ANY   = 5

def bg_usb3_simple_match_config (beagle, trigger_mask, extout_mask, extout_mode, extin_edge_mask, tx_ips_type, rx_ips_type):
    """usage: int return = bg_usb3_simple_match_config(Beagle beagle, u32 trigger_mask, u32 extout_mask, BeagleUsb3ExtoutMode extout_mode, u08 extin_edge_mask, BeagleUsb3IPSType tx_ips_type, BeagleUsb3IPSType rx_ips_type)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_usb3_simple_match_config(beagle, trigger_mask, extout_mask, extout_mode, extin_edge_mask, tx_ips_type, rx_ips_type)


# USB 3.0 Complex matching enable/disable
def bg_usb3_complex_match_enable (beagle):
    """usage: int return = bg_usb3_complex_match_enable(Beagle beagle)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_usb3_complex_match_enable(beagle)


def bg_usb3_complex_match_disable (beagle):
    """usage: int return = bg_usb3_complex_match_disable(Beagle beagle)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_usb3_complex_match_disable(beagle)


# enum BeagleUsbSource
BG_USB_SOURCE_USB3_ASYNC = 0
BG_USB_SOURCE_USB3_RX    = 1
BG_USB_SOURCE_USB3_TX    = 2
BG_USB_SOURCE_USB2       = 3
BG_USB_SOURCE_IV_MON     = 4

class BeagleUsb3DataProperties:
    def __init__ (self):
        self.source_match_type    = 0
        self.source_match_val     = 0
        self.ep_match_type        = 0
        self.ep_match_val         = 0
        self.dev_match_type       = 0
        self.dev_match_val        = 0
        self.stream_id_match_type = 0
        self.stream_id_match_val  = 0
        self.data_len_match_type  = 0
        self.data_len_match_val   = 0

# enum BeagleUsb3PacketType
BG_USB3_MATCH_PACKET_SLC         = 0
BG_USB3_MATCH_PACKET_SHP         = 1
BG_USB3_MATCH_PACKET_SDP         = 2
BG_USB3_MATCH_PACKET_SHP_SDP     = 3
BG_USB3_MATCH_PACKET_TSx         = 4
BG_USB3_MATCH_PACKET_TSEQ        = 5
BG_USB3_MATCH_PACKET_ERROR       = 6
BG_USB3_MATCH_PACKET_5GBIT_START = 7
BG_USB3_MATCH_PACKET_5GBIT_STOP  = 8

# enum BeagleUsb3ErrorType
BG_USB3_MATCH_CRC_DONT_CARE    =    0
BG_USB3_MATCH_CRC_1_VALID      =    1
BG_USB3_MATCH_CRC_2_VALID      =    2
BG_USB3_MATCH_CRC_BOTH_VALID   =    3
BG_USB3_MATCH_CRC_EITHER_FAIL  =    4
BG_USB3_MATCH_CRC_1_FAIL       =    5
BG_USB3_MATCH_CRC_2_FAIL       =    6
BG_USB3_MATCH_CRC_BOTH_FAIL    =    7
BG_USB3_MATCH_ERR_MASK_CRC     = 0x10
BG_USB3_MATCH_ERR_MASK_FRAMING = 0x20
BG_USB3_MATCH_ERR_MASK_UNKNOWN = 0x40

# enum BeagleUsb3MatchModifier
BG_USB3_MATCH_MODIFIER_0 = 0
BG_USB3_MATCH_MODIFIER_1 = 1
BG_USB3_MATCH_MODIFIER_2 = 2
BG_USB3_MATCH_MODIFIER_3 = 3

class BeagleUsb3DataMatchUnit:
    def __init__ (self):
        self.packet_type           = 0
        self.data                  = array('B')
        self.data_valid            = array('B')
        self.err_match             = 0
        self.data_properties_valid = 0
        self.data_properties       = BeagleUsb3DataProperties()
        self.match_modifier        = 0
        self.repeat_count          = 0
        self.sticky_action         = 0
        self.action_mask           = 0
        self.goto_selector         = 0

class BeagleUsb3TimerMatchUnit:
    def __init__ (self):
        self.timer_unit    = 0
        self.timer_val     = 0
        self.action_mask   = 0
        self.goto_selector = 0

# enum BeagleUsb3AsyncEventType
BG_USB3_COMPLEX_MATCH_EVENT_SSTX_LFPS     =  0
BG_USB3_COMPLEX_MATCH_EVENT_SSTX_POLARITY =  1
BG_USB3_COMPLEX_MATCH_EVENT_SSTX_DETECTED =  2
BG_USB3_COMPLEX_MATCH_EVENT_SSTX_SCRAMBLE =  3
BG_USB3_COMPLEX_MATCH_EVENT_SSRX_LFPS     =  4
BG_USB3_COMPLEX_MATCH_EVENT_SSRX_POLARITY =  5
BG_USB3_COMPLEX_MATCH_EVENT_SSRX_DETECTED =  6
BG_USB3_COMPLEX_MATCH_EVENT_SSRX_SCRAMBLE =  7
BG_USB3_COMPLEX_MATCH_EVENT_CROSS_TRIGGER =  8

BG_USB3_COMPLEX_MATCH_EVENT_VBUS_PRESENT  = 11
BG_USB3_COMPLEX_MATCH_EVENT_SSTX_PHYERR   = 12
BG_USB3_COMPLEX_MATCH_EVENT_SSRX_PHYERR   = 13
BG_USB3_COMPLEX_MATCH_EVENT_SMA_EXTIN     = 14

class BeagleUsb3AsyncEventMatchUnit:
    def __init__ (self):
        self.event_type    = 0
        self.edge_mask     = 0
        self.repeat_count  = 0
        self.sticky_action = 0
        self.action_mask   = 0
        self.goto_selector = 0

class BeagleUsb3ComplexMatchState:
    def __init__ (self):
        self.tx_data_0_valid = 0
        self.tx_data_0       = BeagleUsb3DataMatchUnit()
        self.tx_data_1_valid = 0
        self.tx_data_1       = BeagleUsb3DataMatchUnit()
        self.tx_data_2_valid = 0
        self.tx_data_2       = BeagleUsb3DataMatchUnit()
        self.rx_data_0_valid = 0
        self.rx_data_0       = BeagleUsb3DataMatchUnit()
        self.rx_data_1_valid = 0
        self.rx_data_1       = BeagleUsb3DataMatchUnit()
        self.rx_data_2_valid = 0
        self.rx_data_2       = BeagleUsb3DataMatchUnit()
        self.timer_valid     = 0
        self.timer           = BeagleUsb3TimerMatchUnit()
        self.async_valid     = 0
        self.async           = BeagleUsb3AsyncEventMatchUnit()
        self.goto_0          = 0
        self.goto_1          = 0
        self.goto_2          = 0

# Complex matching configuration
def bg_usb3_complex_match_config (beagle, validate, extout, state_0, state_1, state_2, state_3, state_4, state_5, state_6, state_7):
    """usage: int return = bg_usb3_complex_match_config(Beagle beagle, u08 validate, u08 extout, BeagleUsb3ComplexMatchState state_0, BeagleUsb3ComplexMatchState state_1, BeagleUsb3ComplexMatchState state_2, BeagleUsb3ComplexMatchState state_3, BeagleUsb3ComplexMatchState state_4, BeagleUsb3ComplexMatchState state_5, BeagleUsb3ComplexMatchState state_6, BeagleUsb3ComplexMatchState state_7)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # state_0 pre-processing
    c_state_0 = None
    if state_0 != None:
        c_state_0 = (state_0.tx_data_0_valid, state_0.tx_data_0.packet_type, state_0.tx_data_0.data.buffer_info(), state_0.tx_data_0.data_valid.buffer_info(), state_0.tx_data_0.err_match, state_0.tx_data_0.data_properties_valid, state_0.tx_data_0.data_properties.source_match_type, state_0.tx_data_0.data_properties.source_match_val, state_0.tx_data_0.data_properties.ep_match_type, state_0.tx_data_0.data_properties.ep_match_val, state_0.tx_data_0.data_properties.dev_match_type, state_0.tx_data_0.data_properties.dev_match_val, state_0.tx_data_0.data_properties.stream_id_match_type, state_0.tx_data_0.data_properties.stream_id_match_val, state_0.tx_data_0.data_properties.data_len_match_type, state_0.tx_data_0.data_properties.data_len_match_val, state_0.tx_data_0.match_modifier, state_0.tx_data_0.repeat_count, state_0.tx_data_0.sticky_action, state_0.tx_data_0.action_mask, state_0.tx_data_0.goto_selector, state_0.tx_data_1_valid, state_0.tx_data_1.packet_type, state_0.tx_data_1.data.buffer_info(), state_0.tx_data_1.data_valid.buffer_info(), state_0.tx_data_1.err_match, state_0.tx_data_1.data_properties_valid, state_0.tx_data_1.data_properties.source_match_type, state_0.tx_data_1.data_properties.source_match_val, state_0.tx_data_1.data_properties.ep_match_type, state_0.tx_data_1.data_properties.ep_match_val, state_0.tx_data_1.data_properties.dev_match_type, state_0.tx_data_1.data_properties.dev_match_val, state_0.tx_data_1.data_properties.stream_id_match_type, state_0.tx_data_1.data_properties.stream_id_match_val, state_0.tx_data_1.data_properties.data_len_match_type, state_0.tx_data_1.data_properties.data_len_match_val, state_0.tx_data_1.match_modifier, state_0.tx_data_1.repeat_count, state_0.tx_data_1.sticky_action, state_0.tx_data_1.action_mask, state_0.tx_data_1.goto_selector, state_0.tx_data_2_valid, state_0.tx_data_2.packet_type, state_0.tx_data_2.data.buffer_info(), state_0.tx_data_2.data_valid.buffer_info(), state_0.tx_data_2.err_match, state_0.tx_data_2.data_properties_valid, state_0.tx_data_2.data_properties.source_match_type, state_0.tx_data_2.data_properties.source_match_val, state_0.tx_data_2.data_properties.ep_match_type, state_0.tx_data_2.data_properties.ep_match_val, state_0.tx_data_2.data_properties.dev_match_type, state_0.tx_data_2.data_properties.dev_match_val, state_0.tx_data_2.data_properties.stream_id_match_type, state_0.tx_data_2.data_properties.stream_id_match_val, state_0.tx_data_2.data_properties.data_len_match_type, state_0.tx_data_2.data_properties.data_len_match_val, state_0.tx_data_2.match_modifier, state_0.tx_data_2.repeat_count, state_0.tx_data_2.sticky_action, state_0.tx_data_2.action_mask, state_0.tx_data_2.goto_selector, state_0.rx_data_0_valid, state_0.rx_data_0.packet_type, state_0.rx_data_0.data.buffer_info(), state_0.rx_data_0.data_valid.buffer_info(), state_0.rx_data_0.err_match, state_0.rx_data_0.data_properties_valid, state_0.rx_data_0.data_properties.source_match_type, state_0.rx_data_0.data_properties.source_match_val, state_0.rx_data_0.data_properties.ep_match_type, state_0.rx_data_0.data_properties.ep_match_val, state_0.rx_data_0.data_properties.dev_match_type, state_0.rx_data_0.data_properties.dev_match_val, state_0.rx_data_0.data_properties.stream_id_match_type, state_0.rx_data_0.data_properties.stream_id_match_val, state_0.rx_data_0.data_properties.data_len_match_type, state_0.rx_data_0.data_properties.data_len_match_val, state_0.rx_data_0.match_modifier, state_0.rx_data_0.repeat_count, state_0.rx_data_0.sticky_action, state_0.rx_data_0.action_mask, state_0.rx_data_0.goto_selector, state_0.rx_data_1_valid, state_0.rx_data_1.packet_type, state_0.rx_data_1.data.buffer_info(), state_0.rx_data_1.data_valid.buffer_info(), state_0.rx_data_1.err_match, state_0.rx_data_1.data_properties_valid, state_0.rx_data_1.data_properties.source_match_type, state_0.rx_data_1.data_properties.source_match_val, state_0.rx_data_1.data_properties.ep_match_type, state_0.rx_data_1.data_properties.ep_match_val, state_0.rx_data_1.data_properties.dev_match_type, state_0.rx_data_1.data_properties.dev_match_val, state_0.rx_data_1.data_properties.stream_id_match_type, state_0.rx_data_1.data_properties.stream_id_match_val, state_0.rx_data_1.data_properties.data_len_match_type, state_0.rx_data_1.data_properties.data_len_match_val, state_0.rx_data_1.match_modifier, state_0.rx_data_1.repeat_count, state_0.rx_data_1.sticky_action, state_0.rx_data_1.action_mask, state_0.rx_data_1.goto_selector, state_0.rx_data_2_valid, state_0.rx_data_2.packet_type, state_0.rx_data_2.data.buffer_info(), state_0.rx_data_2.data_valid.buffer_info(), state_0.rx_data_2.err_match, state_0.rx_data_2.data_properties_valid, state_0.rx_data_2.data_properties.source_match_type, state_0.rx_data_2.data_properties.source_match_val, state_0.rx_data_2.data_properties.ep_match_type, state_0.rx_data_2.data_properties.ep_match_val, state_0.rx_data_2.data_properties.dev_match_type, state_0.rx_data_2.data_properties.dev_match_val, state_0.rx_data_2.data_properties.stream_id_match_type, state_0.rx_data_2.data_properties.stream_id_match_val, state_0.rx_data_2.data_properties.data_len_match_type, state_0.rx_data_2.data_properties.data_len_match_val, state_0.rx_data_2.match_modifier, state_0.rx_data_2.repeat_count, state_0.rx_data_2.sticky_action, state_0.rx_data_2.action_mask, state_0.rx_data_2.goto_selector, state_0.timer_valid, state_0.timer.timer_unit, state_0.timer.timer_val, state_0.timer.action_mask, state_0.timer.goto_selector, state_0.async_valid, state_0.async.event_type, state_0.async.edge_mask, state_0.async.repeat_count, state_0.async.sticky_action, state_0.async.action_mask, state_0.async.goto_selector, state_0.goto_0, state_0.goto_1, state_0.goto_2)
    # state_1 pre-processing
    c_state_1 = None
    if state_1 != None:
        c_state_1 = (state_1.tx_data_0_valid, state_1.tx_data_0.packet_type, state_1.tx_data_0.data.buffer_info(), state_1.tx_data_0.data_valid.buffer_info(), state_1.tx_data_0.err_match, state_1.tx_data_0.data_properties_valid, state_1.tx_data_0.data_properties.source_match_type, state_1.tx_data_0.data_properties.source_match_val, state_1.tx_data_0.data_properties.ep_match_type, state_1.tx_data_0.data_properties.ep_match_val, state_1.tx_data_0.data_properties.dev_match_type, state_1.tx_data_0.data_properties.dev_match_val, state_1.tx_data_0.data_properties.stream_id_match_type, state_1.tx_data_0.data_properties.stream_id_match_val, state_1.tx_data_0.data_properties.data_len_match_type, state_1.tx_data_0.data_properties.data_len_match_val, state_1.tx_data_0.match_modifier, state_1.tx_data_0.repeat_count, state_1.tx_data_0.sticky_action, state_1.tx_data_0.action_mask, state_1.tx_data_0.goto_selector, state_1.tx_data_1_valid, state_1.tx_data_1.packet_type, state_1.tx_data_1.data.buffer_info(), state_1.tx_data_1.data_valid.buffer_info(), state_1.tx_data_1.err_match, state_1.tx_data_1.data_properties_valid, state_1.tx_data_1.data_properties.source_match_type, state_1.tx_data_1.data_properties.source_match_val, state_1.tx_data_1.data_properties.ep_match_type, state_1.tx_data_1.data_properties.ep_match_val, state_1.tx_data_1.data_properties.dev_match_type, state_1.tx_data_1.data_properties.dev_match_val, state_1.tx_data_1.data_properties.stream_id_match_type, state_1.tx_data_1.data_properties.stream_id_match_val, state_1.tx_data_1.data_properties.data_len_match_type, state_1.tx_data_1.data_properties.data_len_match_val, state_1.tx_data_1.match_modifier, state_1.tx_data_1.repeat_count, state_1.tx_data_1.sticky_action, state_1.tx_data_1.action_mask, state_1.tx_data_1.goto_selector, state_1.tx_data_2_valid, state_1.tx_data_2.packet_type, state_1.tx_data_2.data.buffer_info(), state_1.tx_data_2.data_valid.buffer_info(), state_1.tx_data_2.err_match, state_1.tx_data_2.data_properties_valid, state_1.tx_data_2.data_properties.source_match_type, state_1.tx_data_2.data_properties.source_match_val, state_1.tx_data_2.data_properties.ep_match_type, state_1.tx_data_2.data_properties.ep_match_val, state_1.tx_data_2.data_properties.dev_match_type, state_1.tx_data_2.data_properties.dev_match_val, state_1.tx_data_2.data_properties.stream_id_match_type, state_1.tx_data_2.data_properties.stream_id_match_val, state_1.tx_data_2.data_properties.data_len_match_type, state_1.tx_data_2.data_properties.data_len_match_val, state_1.tx_data_2.match_modifier, state_1.tx_data_2.repeat_count, state_1.tx_data_2.sticky_action, state_1.tx_data_2.action_mask, state_1.tx_data_2.goto_selector, state_1.rx_data_0_valid, state_1.rx_data_0.packet_type, state_1.rx_data_0.data.buffer_info(), state_1.rx_data_0.data_valid.buffer_info(), state_1.rx_data_0.err_match, state_1.rx_data_0.data_properties_valid, state_1.rx_data_0.data_properties.source_match_type, state_1.rx_data_0.data_properties.source_match_val, state_1.rx_data_0.data_properties.ep_match_type, state_1.rx_data_0.data_properties.ep_match_val, state_1.rx_data_0.data_properties.dev_match_type, state_1.rx_data_0.data_properties.dev_match_val, state_1.rx_data_0.data_properties.stream_id_match_type, state_1.rx_data_0.data_properties.stream_id_match_val, state_1.rx_data_0.data_properties.data_len_match_type, state_1.rx_data_0.data_properties.data_len_match_val, state_1.rx_data_0.match_modifier, state_1.rx_data_0.repeat_count, state_1.rx_data_0.sticky_action, state_1.rx_data_0.action_mask, state_1.rx_data_0.goto_selector, state_1.rx_data_1_valid, state_1.rx_data_1.packet_type, state_1.rx_data_1.data.buffer_info(), state_1.rx_data_1.data_valid.buffer_info(), state_1.rx_data_1.err_match, state_1.rx_data_1.data_properties_valid, state_1.rx_data_1.data_properties.source_match_type, state_1.rx_data_1.data_properties.source_match_val, state_1.rx_data_1.data_properties.ep_match_type, state_1.rx_data_1.data_properties.ep_match_val, state_1.rx_data_1.data_properties.dev_match_type, state_1.rx_data_1.data_properties.dev_match_val, state_1.rx_data_1.data_properties.stream_id_match_type, state_1.rx_data_1.data_properties.stream_id_match_val, state_1.rx_data_1.data_properties.data_len_match_type, state_1.rx_data_1.data_properties.data_len_match_val, state_1.rx_data_1.match_modifier, state_1.rx_data_1.repeat_count, state_1.rx_data_1.sticky_action, state_1.rx_data_1.action_mask, state_1.rx_data_1.goto_selector, state_1.rx_data_2_valid, state_1.rx_data_2.packet_type, state_1.rx_data_2.data.buffer_info(), state_1.rx_data_2.data_valid.buffer_info(), state_1.rx_data_2.err_match, state_1.rx_data_2.data_properties_valid, state_1.rx_data_2.data_properties.source_match_type, state_1.rx_data_2.data_properties.source_match_val, state_1.rx_data_2.data_properties.ep_match_type, state_1.rx_data_2.data_properties.ep_match_val, state_1.rx_data_2.data_properties.dev_match_type, state_1.rx_data_2.data_properties.dev_match_val, state_1.rx_data_2.data_properties.stream_id_match_type, state_1.rx_data_2.data_properties.stream_id_match_val, state_1.rx_data_2.data_properties.data_len_match_type, state_1.rx_data_2.data_properties.data_len_match_val, state_1.rx_data_2.match_modifier, state_1.rx_data_2.repeat_count, state_1.rx_data_2.sticky_action, state_1.rx_data_2.action_mask, state_1.rx_data_2.goto_selector, state_1.timer_valid, state_1.timer.timer_unit, state_1.timer.timer_val, state_1.timer.action_mask, state_1.timer.goto_selector, state_1.async_valid, state_1.async.event_type, state_1.async.edge_mask, state_1.async.repeat_count, state_1.async.sticky_action, state_1.async.action_mask, state_1.async.goto_selector, state_1.goto_0, state_1.goto_1, state_1.goto_2)
    # state_2 pre-processing
    c_state_2 = None
    if state_2 != None:
        c_state_2 = (state_2.tx_data_0_valid, state_2.tx_data_0.packet_type, state_2.tx_data_0.data.buffer_info(), state_2.tx_data_0.data_valid.buffer_info(), state_2.tx_data_0.err_match, state_2.tx_data_0.data_properties_valid, state_2.tx_data_0.data_properties.source_match_type, state_2.tx_data_0.data_properties.source_match_val, state_2.tx_data_0.data_properties.ep_match_type, state_2.tx_data_0.data_properties.ep_match_val, state_2.tx_data_0.data_properties.dev_match_type, state_2.tx_data_0.data_properties.dev_match_val, state_2.tx_data_0.data_properties.stream_id_match_type, state_2.tx_data_0.data_properties.stream_id_match_val, state_2.tx_data_0.data_properties.data_len_match_type, state_2.tx_data_0.data_properties.data_len_match_val, state_2.tx_data_0.match_modifier, state_2.tx_data_0.repeat_count, state_2.tx_data_0.sticky_action, state_2.tx_data_0.action_mask, state_2.tx_data_0.goto_selector, state_2.tx_data_1_valid, state_2.tx_data_1.packet_type, state_2.tx_data_1.data.buffer_info(), state_2.tx_data_1.data_valid.buffer_info(), state_2.tx_data_1.err_match, state_2.tx_data_1.data_properties_valid, state_2.tx_data_1.data_properties.source_match_type, state_2.tx_data_1.data_properties.source_match_val, state_2.tx_data_1.data_properties.ep_match_type, state_2.tx_data_1.data_properties.ep_match_val, state_2.tx_data_1.data_properties.dev_match_type, state_2.tx_data_1.data_properties.dev_match_val, state_2.tx_data_1.data_properties.stream_id_match_type, state_2.tx_data_1.data_properties.stream_id_match_val, state_2.tx_data_1.data_properties.data_len_match_type, state_2.tx_data_1.data_properties.data_len_match_val, state_2.tx_data_1.match_modifier, state_2.tx_data_1.repeat_count, state_2.tx_data_1.sticky_action, state_2.tx_data_1.action_mask, state_2.tx_data_1.goto_selector, state_2.tx_data_2_valid, state_2.tx_data_2.packet_type, state_2.tx_data_2.data.buffer_info(), state_2.tx_data_2.data_valid.buffer_info(), state_2.tx_data_2.err_match, state_2.tx_data_2.data_properties_valid, state_2.tx_data_2.data_properties.source_match_type, state_2.tx_data_2.data_properties.source_match_val, state_2.tx_data_2.data_properties.ep_match_type, state_2.tx_data_2.data_properties.ep_match_val, state_2.tx_data_2.data_properties.dev_match_type, state_2.tx_data_2.data_properties.dev_match_val, state_2.tx_data_2.data_properties.stream_id_match_type, state_2.tx_data_2.data_properties.stream_id_match_val, state_2.tx_data_2.data_properties.data_len_match_type, state_2.tx_data_2.data_properties.data_len_match_val, state_2.tx_data_2.match_modifier, state_2.tx_data_2.repeat_count, state_2.tx_data_2.sticky_action, state_2.tx_data_2.action_mask, state_2.tx_data_2.goto_selector, state_2.rx_data_0_valid, state_2.rx_data_0.packet_type, state_2.rx_data_0.data.buffer_info(), state_2.rx_data_0.data_valid.buffer_info(), state_2.rx_data_0.err_match, state_2.rx_data_0.data_properties_valid, state_2.rx_data_0.data_properties.source_match_type, state_2.rx_data_0.data_properties.source_match_val, state_2.rx_data_0.data_properties.ep_match_type, state_2.rx_data_0.data_properties.ep_match_val, state_2.rx_data_0.data_properties.dev_match_type, state_2.rx_data_0.data_properties.dev_match_val, state_2.rx_data_0.data_properties.stream_id_match_type, state_2.rx_data_0.data_properties.stream_id_match_val, state_2.rx_data_0.data_properties.data_len_match_type, state_2.rx_data_0.data_properties.data_len_match_val, state_2.rx_data_0.match_modifier, state_2.rx_data_0.repeat_count, state_2.rx_data_0.sticky_action, state_2.rx_data_0.action_mask, state_2.rx_data_0.goto_selector, state_2.rx_data_1_valid, state_2.rx_data_1.packet_type, state_2.rx_data_1.data.buffer_info(), state_2.rx_data_1.data_valid.buffer_info(), state_2.rx_data_1.err_match, state_2.rx_data_1.data_properties_valid, state_2.rx_data_1.data_properties.source_match_type, state_2.rx_data_1.data_properties.source_match_val, state_2.rx_data_1.data_properties.ep_match_type, state_2.rx_data_1.data_properties.ep_match_val, state_2.rx_data_1.data_properties.dev_match_type, state_2.rx_data_1.data_properties.dev_match_val, state_2.rx_data_1.data_properties.stream_id_match_type, state_2.rx_data_1.data_properties.stream_id_match_val, state_2.rx_data_1.data_properties.data_len_match_type, state_2.rx_data_1.data_properties.data_len_match_val, state_2.rx_data_1.match_modifier, state_2.rx_data_1.repeat_count, state_2.rx_data_1.sticky_action, state_2.rx_data_1.action_mask, state_2.rx_data_1.goto_selector, state_2.rx_data_2_valid, state_2.rx_data_2.packet_type, state_2.rx_data_2.data.buffer_info(), state_2.rx_data_2.data_valid.buffer_info(), state_2.rx_data_2.err_match, state_2.rx_data_2.data_properties_valid, state_2.rx_data_2.data_properties.source_match_type, state_2.rx_data_2.data_properties.source_match_val, state_2.rx_data_2.data_properties.ep_match_type, state_2.rx_data_2.data_properties.ep_match_val, state_2.rx_data_2.data_properties.dev_match_type, state_2.rx_data_2.data_properties.dev_match_val, state_2.rx_data_2.data_properties.stream_id_match_type, state_2.rx_data_2.data_properties.stream_id_match_val, state_2.rx_data_2.data_properties.data_len_match_type, state_2.rx_data_2.data_properties.data_len_match_val, state_2.rx_data_2.match_modifier, state_2.rx_data_2.repeat_count, state_2.rx_data_2.sticky_action, state_2.rx_data_2.action_mask, state_2.rx_data_2.goto_selector, state_2.timer_valid, state_2.timer.timer_unit, state_2.timer.timer_val, state_2.timer.action_mask, state_2.timer.goto_selector, state_2.async_valid, state_2.async.event_type, state_2.async.edge_mask, state_2.async.repeat_count, state_2.async.sticky_action, state_2.async.action_mask, state_2.async.goto_selector, state_2.goto_0, state_2.goto_1, state_2.goto_2)
    # state_3 pre-processing
    c_state_3 = None
    if state_3 != None:
        c_state_3 = (state_3.tx_data_0_valid, state_3.tx_data_0.packet_type, state_3.tx_data_0.data.buffer_info(), state_3.tx_data_0.data_valid.buffer_info(), state_3.tx_data_0.err_match, state_3.tx_data_0.data_properties_valid, state_3.tx_data_0.data_properties.source_match_type, state_3.tx_data_0.data_properties.source_match_val, state_3.tx_data_0.data_properties.ep_match_type, state_3.tx_data_0.data_properties.ep_match_val, state_3.tx_data_0.data_properties.dev_match_type, state_3.tx_data_0.data_properties.dev_match_val, state_3.tx_data_0.data_properties.stream_id_match_type, state_3.tx_data_0.data_properties.stream_id_match_val, state_3.tx_data_0.data_properties.data_len_match_type, state_3.tx_data_0.data_properties.data_len_match_val, state_3.tx_data_0.match_modifier, state_3.tx_data_0.repeat_count, state_3.tx_data_0.sticky_action, state_3.tx_data_0.action_mask, state_3.tx_data_0.goto_selector, state_3.tx_data_1_valid, state_3.tx_data_1.packet_type, state_3.tx_data_1.data.buffer_info(), state_3.tx_data_1.data_valid.buffer_info(), state_3.tx_data_1.err_match, state_3.tx_data_1.data_properties_valid, state_3.tx_data_1.data_properties.source_match_type, state_3.tx_data_1.data_properties.source_match_val, state_3.tx_data_1.data_properties.ep_match_type, state_3.tx_data_1.data_properties.ep_match_val, state_3.tx_data_1.data_properties.dev_match_type, state_3.tx_data_1.data_properties.dev_match_val, state_3.tx_data_1.data_properties.stream_id_match_type, state_3.tx_data_1.data_properties.stream_id_match_val, state_3.tx_data_1.data_properties.data_len_match_type, state_3.tx_data_1.data_properties.data_len_match_val, state_3.tx_data_1.match_modifier, state_3.tx_data_1.repeat_count, state_3.tx_data_1.sticky_action, state_3.tx_data_1.action_mask, state_3.tx_data_1.goto_selector, state_3.tx_data_2_valid, state_3.tx_data_2.packet_type, state_3.tx_data_2.data.buffer_info(), state_3.tx_data_2.data_valid.buffer_info(), state_3.tx_data_2.err_match, state_3.tx_data_2.data_properties_valid, state_3.tx_data_2.data_properties.source_match_type, state_3.tx_data_2.data_properties.source_match_val, state_3.tx_data_2.data_properties.ep_match_type, state_3.tx_data_2.data_properties.ep_match_val, state_3.tx_data_2.data_properties.dev_match_type, state_3.tx_data_2.data_properties.dev_match_val, state_3.tx_data_2.data_properties.stream_id_match_type, state_3.tx_data_2.data_properties.stream_id_match_val, state_3.tx_data_2.data_properties.data_len_match_type, state_3.tx_data_2.data_properties.data_len_match_val, state_3.tx_data_2.match_modifier, state_3.tx_data_2.repeat_count, state_3.tx_data_2.sticky_action, state_3.tx_data_2.action_mask, state_3.tx_data_2.goto_selector, state_3.rx_data_0_valid, state_3.rx_data_0.packet_type, state_3.rx_data_0.data.buffer_info(), state_3.rx_data_0.data_valid.buffer_info(), state_3.rx_data_0.err_match, state_3.rx_data_0.data_properties_valid, state_3.rx_data_0.data_properties.source_match_type, state_3.rx_data_0.data_properties.source_match_val, state_3.rx_data_0.data_properties.ep_match_type, state_3.rx_data_0.data_properties.ep_match_val, state_3.rx_data_0.data_properties.dev_match_type, state_3.rx_data_0.data_properties.dev_match_val, state_3.rx_data_0.data_properties.stream_id_match_type, state_3.rx_data_0.data_properties.stream_id_match_val, state_3.rx_data_0.data_properties.data_len_match_type, state_3.rx_data_0.data_properties.data_len_match_val, state_3.rx_data_0.match_modifier, state_3.rx_data_0.repeat_count, state_3.rx_data_0.sticky_action, state_3.rx_data_0.action_mask, state_3.rx_data_0.goto_selector, state_3.rx_data_1_valid, state_3.rx_data_1.packet_type, state_3.rx_data_1.data.buffer_info(), state_3.rx_data_1.data_valid.buffer_info(), state_3.rx_data_1.err_match, state_3.rx_data_1.data_properties_valid, state_3.rx_data_1.data_properties.source_match_type, state_3.rx_data_1.data_properties.source_match_val, state_3.rx_data_1.data_properties.ep_match_type, state_3.rx_data_1.data_properties.ep_match_val, state_3.rx_data_1.data_properties.dev_match_type, state_3.rx_data_1.data_properties.dev_match_val, state_3.rx_data_1.data_properties.stream_id_match_type, state_3.rx_data_1.data_properties.stream_id_match_val, state_3.rx_data_1.data_properties.data_len_match_type, state_3.rx_data_1.data_properties.data_len_match_val, state_3.rx_data_1.match_modifier, state_3.rx_data_1.repeat_count, state_3.rx_data_1.sticky_action, state_3.rx_data_1.action_mask, state_3.rx_data_1.goto_selector, state_3.rx_data_2_valid, state_3.rx_data_2.packet_type, state_3.rx_data_2.data.buffer_info(), state_3.rx_data_2.data_valid.buffer_info(), state_3.rx_data_2.err_match, state_3.rx_data_2.data_properties_valid, state_3.rx_data_2.data_properties.source_match_type, state_3.rx_data_2.data_properties.source_match_val, state_3.rx_data_2.data_properties.ep_match_type, state_3.rx_data_2.data_properties.ep_match_val, state_3.rx_data_2.data_properties.dev_match_type, state_3.rx_data_2.data_properties.dev_match_val, state_3.rx_data_2.data_properties.stream_id_match_type, state_3.rx_data_2.data_properties.stream_id_match_val, state_3.rx_data_2.data_properties.data_len_match_type, state_3.rx_data_2.data_properties.data_len_match_val, state_3.rx_data_2.match_modifier, state_3.rx_data_2.repeat_count, state_3.rx_data_2.sticky_action, state_3.rx_data_2.action_mask, state_3.rx_data_2.goto_selector, state_3.timer_valid, state_3.timer.timer_unit, state_3.timer.timer_val, state_3.timer.action_mask, state_3.timer.goto_selector, state_3.async_valid, state_3.async.event_type, state_3.async.edge_mask, state_3.async.repeat_count, state_3.async.sticky_action, state_3.async.action_mask, state_3.async.goto_selector, state_3.goto_0, state_3.goto_1, state_3.goto_2)
    # state_4 pre-processing
    c_state_4 = None
    if state_4 != None:
        c_state_4 = (state_4.tx_data_0_valid, state_4.tx_data_0.packet_type, state_4.tx_data_0.data.buffer_info(), state_4.tx_data_0.data_valid.buffer_info(), state_4.tx_data_0.err_match, state_4.tx_data_0.data_properties_valid, state_4.tx_data_0.data_properties.source_match_type, state_4.tx_data_0.data_properties.source_match_val, state_4.tx_data_0.data_properties.ep_match_type, state_4.tx_data_0.data_properties.ep_match_val, state_4.tx_data_0.data_properties.dev_match_type, state_4.tx_data_0.data_properties.dev_match_val, state_4.tx_data_0.data_properties.stream_id_match_type, state_4.tx_data_0.data_properties.stream_id_match_val, state_4.tx_data_0.data_properties.data_len_match_type, state_4.tx_data_0.data_properties.data_len_match_val, state_4.tx_data_0.match_modifier, state_4.tx_data_0.repeat_count, state_4.tx_data_0.sticky_action, state_4.tx_data_0.action_mask, state_4.tx_data_0.goto_selector, state_4.tx_data_1_valid, state_4.tx_data_1.packet_type, state_4.tx_data_1.data.buffer_info(), state_4.tx_data_1.data_valid.buffer_info(), state_4.tx_data_1.err_match, state_4.tx_data_1.data_properties_valid, state_4.tx_data_1.data_properties.source_match_type, state_4.tx_data_1.data_properties.source_match_val, state_4.tx_data_1.data_properties.ep_match_type, state_4.tx_data_1.data_properties.ep_match_val, state_4.tx_data_1.data_properties.dev_match_type, state_4.tx_data_1.data_properties.dev_match_val, state_4.tx_data_1.data_properties.stream_id_match_type, state_4.tx_data_1.data_properties.stream_id_match_val, state_4.tx_data_1.data_properties.data_len_match_type, state_4.tx_data_1.data_properties.data_len_match_val, state_4.tx_data_1.match_modifier, state_4.tx_data_1.repeat_count, state_4.tx_data_1.sticky_action, state_4.tx_data_1.action_mask, state_4.tx_data_1.goto_selector, state_4.tx_data_2_valid, state_4.tx_data_2.packet_type, state_4.tx_data_2.data.buffer_info(), state_4.tx_data_2.data_valid.buffer_info(), state_4.tx_data_2.err_match, state_4.tx_data_2.data_properties_valid, state_4.tx_data_2.data_properties.source_match_type, state_4.tx_data_2.data_properties.source_match_val, state_4.tx_data_2.data_properties.ep_match_type, state_4.tx_data_2.data_properties.ep_match_val, state_4.tx_data_2.data_properties.dev_match_type, state_4.tx_data_2.data_properties.dev_match_val, state_4.tx_data_2.data_properties.stream_id_match_type, state_4.tx_data_2.data_properties.stream_id_match_val, state_4.tx_data_2.data_properties.data_len_match_type, state_4.tx_data_2.data_properties.data_len_match_val, state_4.tx_data_2.match_modifier, state_4.tx_data_2.repeat_count, state_4.tx_data_2.sticky_action, state_4.tx_data_2.action_mask, state_4.tx_data_2.goto_selector, state_4.rx_data_0_valid, state_4.rx_data_0.packet_type, state_4.rx_data_0.data.buffer_info(), state_4.rx_data_0.data_valid.buffer_info(), state_4.rx_data_0.err_match, state_4.rx_data_0.data_properties_valid, state_4.rx_data_0.data_properties.source_match_type, state_4.rx_data_0.data_properties.source_match_val, state_4.rx_data_0.data_properties.ep_match_type, state_4.rx_data_0.data_properties.ep_match_val, state_4.rx_data_0.data_properties.dev_match_type, state_4.rx_data_0.data_properties.dev_match_val, state_4.rx_data_0.data_properties.stream_id_match_type, state_4.rx_data_0.data_properties.stream_id_match_val, state_4.rx_data_0.data_properties.data_len_match_type, state_4.rx_data_0.data_properties.data_len_match_val, state_4.rx_data_0.match_modifier, state_4.rx_data_0.repeat_count, state_4.rx_data_0.sticky_action, state_4.rx_data_0.action_mask, state_4.rx_data_0.goto_selector, state_4.rx_data_1_valid, state_4.rx_data_1.packet_type, state_4.rx_data_1.data.buffer_info(), state_4.rx_data_1.data_valid.buffer_info(), state_4.rx_data_1.err_match, state_4.rx_data_1.data_properties_valid, state_4.rx_data_1.data_properties.source_match_type, state_4.rx_data_1.data_properties.source_match_val, state_4.rx_data_1.data_properties.ep_match_type, state_4.rx_data_1.data_properties.ep_match_val, state_4.rx_data_1.data_properties.dev_match_type, state_4.rx_data_1.data_properties.dev_match_val, state_4.rx_data_1.data_properties.stream_id_match_type, state_4.rx_data_1.data_properties.stream_id_match_val, state_4.rx_data_1.data_properties.data_len_match_type, state_4.rx_data_1.data_properties.data_len_match_val, state_4.rx_data_1.match_modifier, state_4.rx_data_1.repeat_count, state_4.rx_data_1.sticky_action, state_4.rx_data_1.action_mask, state_4.rx_data_1.goto_selector, state_4.rx_data_2_valid, state_4.rx_data_2.packet_type, state_4.rx_data_2.data.buffer_info(), state_4.rx_data_2.data_valid.buffer_info(), state_4.rx_data_2.err_match, state_4.rx_data_2.data_properties_valid, state_4.rx_data_2.data_properties.source_match_type, state_4.rx_data_2.data_properties.source_match_val, state_4.rx_data_2.data_properties.ep_match_type, state_4.rx_data_2.data_properties.ep_match_val, state_4.rx_data_2.data_properties.dev_match_type, state_4.rx_data_2.data_properties.dev_match_val, state_4.rx_data_2.data_properties.stream_id_match_type, state_4.rx_data_2.data_properties.stream_id_match_val, state_4.rx_data_2.data_properties.data_len_match_type, state_4.rx_data_2.data_properties.data_len_match_val, state_4.rx_data_2.match_modifier, state_4.rx_data_2.repeat_count, state_4.rx_data_2.sticky_action, state_4.rx_data_2.action_mask, state_4.rx_data_2.goto_selector, state_4.timer_valid, state_4.timer.timer_unit, state_4.timer.timer_val, state_4.timer.action_mask, state_4.timer.goto_selector, state_4.async_valid, state_4.async.event_type, state_4.async.edge_mask, state_4.async.repeat_count, state_4.async.sticky_action, state_4.async.action_mask, state_4.async.goto_selector, state_4.goto_0, state_4.goto_1, state_4.goto_2)
    # state_5 pre-processing
    c_state_5 = None
    if state_5 != None:
        c_state_5 = (state_5.tx_data_0_valid, state_5.tx_data_0.packet_type, state_5.tx_data_0.data.buffer_info(), state_5.tx_data_0.data_valid.buffer_info(), state_5.tx_data_0.err_match, state_5.tx_data_0.data_properties_valid, state_5.tx_data_0.data_properties.source_match_type, state_5.tx_data_0.data_properties.source_match_val, state_5.tx_data_0.data_properties.ep_match_type, state_5.tx_data_0.data_properties.ep_match_val, state_5.tx_data_0.data_properties.dev_match_type, state_5.tx_data_0.data_properties.dev_match_val, state_5.tx_data_0.data_properties.stream_id_match_type, state_5.tx_data_0.data_properties.stream_id_match_val, state_5.tx_data_0.data_properties.data_len_match_type, state_5.tx_data_0.data_properties.data_len_match_val, state_5.tx_data_0.match_modifier, state_5.tx_data_0.repeat_count, state_5.tx_data_0.sticky_action, state_5.tx_data_0.action_mask, state_5.tx_data_0.goto_selector, state_5.tx_data_1_valid, state_5.tx_data_1.packet_type, state_5.tx_data_1.data.buffer_info(), state_5.tx_data_1.data_valid.buffer_info(), state_5.tx_data_1.err_match, state_5.tx_data_1.data_properties_valid, state_5.tx_data_1.data_properties.source_match_type, state_5.tx_data_1.data_properties.source_match_val, state_5.tx_data_1.data_properties.ep_match_type, state_5.tx_data_1.data_properties.ep_match_val, state_5.tx_data_1.data_properties.dev_match_type, state_5.tx_data_1.data_properties.dev_match_val, state_5.tx_data_1.data_properties.stream_id_match_type, state_5.tx_data_1.data_properties.stream_id_match_val, state_5.tx_data_1.data_properties.data_len_match_type, state_5.tx_data_1.data_properties.data_len_match_val, state_5.tx_data_1.match_modifier, state_5.tx_data_1.repeat_count, state_5.tx_data_1.sticky_action, state_5.tx_data_1.action_mask, state_5.tx_data_1.goto_selector, state_5.tx_data_2_valid, state_5.tx_data_2.packet_type, state_5.tx_data_2.data.buffer_info(), state_5.tx_data_2.data_valid.buffer_info(), state_5.tx_data_2.err_match, state_5.tx_data_2.data_properties_valid, state_5.tx_data_2.data_properties.source_match_type, state_5.tx_data_2.data_properties.source_match_val, state_5.tx_data_2.data_properties.ep_match_type, state_5.tx_data_2.data_properties.ep_match_val, state_5.tx_data_2.data_properties.dev_match_type, state_5.tx_data_2.data_properties.dev_match_val, state_5.tx_data_2.data_properties.stream_id_match_type, state_5.tx_data_2.data_properties.stream_id_match_val, state_5.tx_data_2.data_properties.data_len_match_type, state_5.tx_data_2.data_properties.data_len_match_val, state_5.tx_data_2.match_modifier, state_5.tx_data_2.repeat_count, state_5.tx_data_2.sticky_action, state_5.tx_data_2.action_mask, state_5.tx_data_2.goto_selector, state_5.rx_data_0_valid, state_5.rx_data_0.packet_type, state_5.rx_data_0.data.buffer_info(), state_5.rx_data_0.data_valid.buffer_info(), state_5.rx_data_0.err_match, state_5.rx_data_0.data_properties_valid, state_5.rx_data_0.data_properties.source_match_type, state_5.rx_data_0.data_properties.source_match_val, state_5.rx_data_0.data_properties.ep_match_type, state_5.rx_data_0.data_properties.ep_match_val, state_5.rx_data_0.data_properties.dev_match_type, state_5.rx_data_0.data_properties.dev_match_val, state_5.rx_data_0.data_properties.stream_id_match_type, state_5.rx_data_0.data_properties.stream_id_match_val, state_5.rx_data_0.data_properties.data_len_match_type, state_5.rx_data_0.data_properties.data_len_match_val, state_5.rx_data_0.match_modifier, state_5.rx_data_0.repeat_count, state_5.rx_data_0.sticky_action, state_5.rx_data_0.action_mask, state_5.rx_data_0.goto_selector, state_5.rx_data_1_valid, state_5.rx_data_1.packet_type, state_5.rx_data_1.data.buffer_info(), state_5.rx_data_1.data_valid.buffer_info(), state_5.rx_data_1.err_match, state_5.rx_data_1.data_properties_valid, state_5.rx_data_1.data_properties.source_match_type, state_5.rx_data_1.data_properties.source_match_val, state_5.rx_data_1.data_properties.ep_match_type, state_5.rx_data_1.data_properties.ep_match_val, state_5.rx_data_1.data_properties.dev_match_type, state_5.rx_data_1.data_properties.dev_match_val, state_5.rx_data_1.data_properties.stream_id_match_type, state_5.rx_data_1.data_properties.stream_id_match_val, state_5.rx_data_1.data_properties.data_len_match_type, state_5.rx_data_1.data_properties.data_len_match_val, state_5.rx_data_1.match_modifier, state_5.rx_data_1.repeat_count, state_5.rx_data_1.sticky_action, state_5.rx_data_1.action_mask, state_5.rx_data_1.goto_selector, state_5.rx_data_2_valid, state_5.rx_data_2.packet_type, state_5.rx_data_2.data.buffer_info(), state_5.rx_data_2.data_valid.buffer_info(), state_5.rx_data_2.err_match, state_5.rx_data_2.data_properties_valid, state_5.rx_data_2.data_properties.source_match_type, state_5.rx_data_2.data_properties.source_match_val, state_5.rx_data_2.data_properties.ep_match_type, state_5.rx_data_2.data_properties.ep_match_val, state_5.rx_data_2.data_properties.dev_match_type, state_5.rx_data_2.data_properties.dev_match_val, state_5.rx_data_2.data_properties.stream_id_match_type, state_5.rx_data_2.data_properties.stream_id_match_val, state_5.rx_data_2.data_properties.data_len_match_type, state_5.rx_data_2.data_properties.data_len_match_val, state_5.rx_data_2.match_modifier, state_5.rx_data_2.repeat_count, state_5.rx_data_2.sticky_action, state_5.rx_data_2.action_mask, state_5.rx_data_2.goto_selector, state_5.timer_valid, state_5.timer.timer_unit, state_5.timer.timer_val, state_5.timer.action_mask, state_5.timer.goto_selector, state_5.async_valid, state_5.async.event_type, state_5.async.edge_mask, state_5.async.repeat_count, state_5.async.sticky_action, state_5.async.action_mask, state_5.async.goto_selector, state_5.goto_0, state_5.goto_1, state_5.goto_2)
    # state_6 pre-processing
    c_state_6 = None
    if state_6 != None:
        c_state_6 = (state_6.tx_data_0_valid, state_6.tx_data_0.packet_type, state_6.tx_data_0.data.buffer_info(), state_6.tx_data_0.data_valid.buffer_info(), state_6.tx_data_0.err_match, state_6.tx_data_0.data_properties_valid, state_6.tx_data_0.data_properties.source_match_type, state_6.tx_data_0.data_properties.source_match_val, state_6.tx_data_0.data_properties.ep_match_type, state_6.tx_data_0.data_properties.ep_match_val, state_6.tx_data_0.data_properties.dev_match_type, state_6.tx_data_0.data_properties.dev_match_val, state_6.tx_data_0.data_properties.stream_id_match_type, state_6.tx_data_0.data_properties.stream_id_match_val, state_6.tx_data_0.data_properties.data_len_match_type, state_6.tx_data_0.data_properties.data_len_match_val, state_6.tx_data_0.match_modifier, state_6.tx_data_0.repeat_count, state_6.tx_data_0.sticky_action, state_6.tx_data_0.action_mask, state_6.tx_data_0.goto_selector, state_6.tx_data_1_valid, state_6.tx_data_1.packet_type, state_6.tx_data_1.data.buffer_info(), state_6.tx_data_1.data_valid.buffer_info(), state_6.tx_data_1.err_match, state_6.tx_data_1.data_properties_valid, state_6.tx_data_1.data_properties.source_match_type, state_6.tx_data_1.data_properties.source_match_val, state_6.tx_data_1.data_properties.ep_match_type, state_6.tx_data_1.data_properties.ep_match_val, state_6.tx_data_1.data_properties.dev_match_type, state_6.tx_data_1.data_properties.dev_match_val, state_6.tx_data_1.data_properties.stream_id_match_type, state_6.tx_data_1.data_properties.stream_id_match_val, state_6.tx_data_1.data_properties.data_len_match_type, state_6.tx_data_1.data_properties.data_len_match_val, state_6.tx_data_1.match_modifier, state_6.tx_data_1.repeat_count, state_6.tx_data_1.sticky_action, state_6.tx_data_1.action_mask, state_6.tx_data_1.goto_selector, state_6.tx_data_2_valid, state_6.tx_data_2.packet_type, state_6.tx_data_2.data.buffer_info(), state_6.tx_data_2.data_valid.buffer_info(), state_6.tx_data_2.err_match, state_6.tx_data_2.data_properties_valid, state_6.tx_data_2.data_properties.source_match_type, state_6.tx_data_2.data_properties.source_match_val, state_6.tx_data_2.data_properties.ep_match_type, state_6.tx_data_2.data_properties.ep_match_val, state_6.tx_data_2.data_properties.dev_match_type, state_6.tx_data_2.data_properties.dev_match_val, state_6.tx_data_2.data_properties.stream_id_match_type, state_6.tx_data_2.data_properties.stream_id_match_val, state_6.tx_data_2.data_properties.data_len_match_type, state_6.tx_data_2.data_properties.data_len_match_val, state_6.tx_data_2.match_modifier, state_6.tx_data_2.repeat_count, state_6.tx_data_2.sticky_action, state_6.tx_data_2.action_mask, state_6.tx_data_2.goto_selector, state_6.rx_data_0_valid, state_6.rx_data_0.packet_type, state_6.rx_data_0.data.buffer_info(), state_6.rx_data_0.data_valid.buffer_info(), state_6.rx_data_0.err_match, state_6.rx_data_0.data_properties_valid, state_6.rx_data_0.data_properties.source_match_type, state_6.rx_data_0.data_properties.source_match_val, state_6.rx_data_0.data_properties.ep_match_type, state_6.rx_data_0.data_properties.ep_match_val, state_6.rx_data_0.data_properties.dev_match_type, state_6.rx_data_0.data_properties.dev_match_val, state_6.rx_data_0.data_properties.stream_id_match_type, state_6.rx_data_0.data_properties.stream_id_match_val, state_6.rx_data_0.data_properties.data_len_match_type, state_6.rx_data_0.data_properties.data_len_match_val, state_6.rx_data_0.match_modifier, state_6.rx_data_0.repeat_count, state_6.rx_data_0.sticky_action, state_6.rx_data_0.action_mask, state_6.rx_data_0.goto_selector, state_6.rx_data_1_valid, state_6.rx_data_1.packet_type, state_6.rx_data_1.data.buffer_info(), state_6.rx_data_1.data_valid.buffer_info(), state_6.rx_data_1.err_match, state_6.rx_data_1.data_properties_valid, state_6.rx_data_1.data_properties.source_match_type, state_6.rx_data_1.data_properties.source_match_val, state_6.rx_data_1.data_properties.ep_match_type, state_6.rx_data_1.data_properties.ep_match_val, state_6.rx_data_1.data_properties.dev_match_type, state_6.rx_data_1.data_properties.dev_match_val, state_6.rx_data_1.data_properties.stream_id_match_type, state_6.rx_data_1.data_properties.stream_id_match_val, state_6.rx_data_1.data_properties.data_len_match_type, state_6.rx_data_1.data_properties.data_len_match_val, state_6.rx_data_1.match_modifier, state_6.rx_data_1.repeat_count, state_6.rx_data_1.sticky_action, state_6.rx_data_1.action_mask, state_6.rx_data_1.goto_selector, state_6.rx_data_2_valid, state_6.rx_data_2.packet_type, state_6.rx_data_2.data.buffer_info(), state_6.rx_data_2.data_valid.buffer_info(), state_6.rx_data_2.err_match, state_6.rx_data_2.data_properties_valid, state_6.rx_data_2.data_properties.source_match_type, state_6.rx_data_2.data_properties.source_match_val, state_6.rx_data_2.data_properties.ep_match_type, state_6.rx_data_2.data_properties.ep_match_val, state_6.rx_data_2.data_properties.dev_match_type, state_6.rx_data_2.data_properties.dev_match_val, state_6.rx_data_2.data_properties.stream_id_match_type, state_6.rx_data_2.data_properties.stream_id_match_val, state_6.rx_data_2.data_properties.data_len_match_type, state_6.rx_data_2.data_properties.data_len_match_val, state_6.rx_data_2.match_modifier, state_6.rx_data_2.repeat_count, state_6.rx_data_2.sticky_action, state_6.rx_data_2.action_mask, state_6.rx_data_2.goto_selector, state_6.timer_valid, state_6.timer.timer_unit, state_6.timer.timer_val, state_6.timer.action_mask, state_6.timer.goto_selector, state_6.async_valid, state_6.async.event_type, state_6.async.edge_mask, state_6.async.repeat_count, state_6.async.sticky_action, state_6.async.action_mask, state_6.async.goto_selector, state_6.goto_0, state_6.goto_1, state_6.goto_2)
    # state_7 pre-processing
    c_state_7 = None
    if state_7 != None:
        c_state_7 = (state_7.tx_data_0_valid, state_7.tx_data_0.packet_type, state_7.tx_data_0.data.buffer_info(), state_7.tx_data_0.data_valid.buffer_info(), state_7.tx_data_0.err_match, state_7.tx_data_0.data_properties_valid, state_7.tx_data_0.data_properties.source_match_type, state_7.tx_data_0.data_properties.source_match_val, state_7.tx_data_0.data_properties.ep_match_type, state_7.tx_data_0.data_properties.ep_match_val, state_7.tx_data_0.data_properties.dev_match_type, state_7.tx_data_0.data_properties.dev_match_val, state_7.tx_data_0.data_properties.stream_id_match_type, state_7.tx_data_0.data_properties.stream_id_match_val, state_7.tx_data_0.data_properties.data_len_match_type, state_7.tx_data_0.data_properties.data_len_match_val, state_7.tx_data_0.match_modifier, state_7.tx_data_0.repeat_count, state_7.tx_data_0.sticky_action, state_7.tx_data_0.action_mask, state_7.tx_data_0.goto_selector, state_7.tx_data_1_valid, state_7.tx_data_1.packet_type, state_7.tx_data_1.data.buffer_info(), state_7.tx_data_1.data_valid.buffer_info(), state_7.tx_data_1.err_match, state_7.tx_data_1.data_properties_valid, state_7.tx_data_1.data_properties.source_match_type, state_7.tx_data_1.data_properties.source_match_val, state_7.tx_data_1.data_properties.ep_match_type, state_7.tx_data_1.data_properties.ep_match_val, state_7.tx_data_1.data_properties.dev_match_type, state_7.tx_data_1.data_properties.dev_match_val, state_7.tx_data_1.data_properties.stream_id_match_type, state_7.tx_data_1.data_properties.stream_id_match_val, state_7.tx_data_1.data_properties.data_len_match_type, state_7.tx_data_1.data_properties.data_len_match_val, state_7.tx_data_1.match_modifier, state_7.tx_data_1.repeat_count, state_7.tx_data_1.sticky_action, state_7.tx_data_1.action_mask, state_7.tx_data_1.goto_selector, state_7.tx_data_2_valid, state_7.tx_data_2.packet_type, state_7.tx_data_2.data.buffer_info(), state_7.tx_data_2.data_valid.buffer_info(), state_7.tx_data_2.err_match, state_7.tx_data_2.data_properties_valid, state_7.tx_data_2.data_properties.source_match_type, state_7.tx_data_2.data_properties.source_match_val, state_7.tx_data_2.data_properties.ep_match_type, state_7.tx_data_2.data_properties.ep_match_val, state_7.tx_data_2.data_properties.dev_match_type, state_7.tx_data_2.data_properties.dev_match_val, state_7.tx_data_2.data_properties.stream_id_match_type, state_7.tx_data_2.data_properties.stream_id_match_val, state_7.tx_data_2.data_properties.data_len_match_type, state_7.tx_data_2.data_properties.data_len_match_val, state_7.tx_data_2.match_modifier, state_7.tx_data_2.repeat_count, state_7.tx_data_2.sticky_action, state_7.tx_data_2.action_mask, state_7.tx_data_2.goto_selector, state_7.rx_data_0_valid, state_7.rx_data_0.packet_type, state_7.rx_data_0.data.buffer_info(), state_7.rx_data_0.data_valid.buffer_info(), state_7.rx_data_0.err_match, state_7.rx_data_0.data_properties_valid, state_7.rx_data_0.data_properties.source_match_type, state_7.rx_data_0.data_properties.source_match_val, state_7.rx_data_0.data_properties.ep_match_type, state_7.rx_data_0.data_properties.ep_match_val, state_7.rx_data_0.data_properties.dev_match_type, state_7.rx_data_0.data_properties.dev_match_val, state_7.rx_data_0.data_properties.stream_id_match_type, state_7.rx_data_0.data_properties.stream_id_match_val, state_7.rx_data_0.data_properties.data_len_match_type, state_7.rx_data_0.data_properties.data_len_match_val, state_7.rx_data_0.match_modifier, state_7.rx_data_0.repeat_count, state_7.rx_data_0.sticky_action, state_7.rx_data_0.action_mask, state_7.rx_data_0.goto_selector, state_7.rx_data_1_valid, state_7.rx_data_1.packet_type, state_7.rx_data_1.data.buffer_info(), state_7.rx_data_1.data_valid.buffer_info(), state_7.rx_data_1.err_match, state_7.rx_data_1.data_properties_valid, state_7.rx_data_1.data_properties.source_match_type, state_7.rx_data_1.data_properties.source_match_val, state_7.rx_data_1.data_properties.ep_match_type, state_7.rx_data_1.data_properties.ep_match_val, state_7.rx_data_1.data_properties.dev_match_type, state_7.rx_data_1.data_properties.dev_match_val, state_7.rx_data_1.data_properties.stream_id_match_type, state_7.rx_data_1.data_properties.stream_id_match_val, state_7.rx_data_1.data_properties.data_len_match_type, state_7.rx_data_1.data_properties.data_len_match_val, state_7.rx_data_1.match_modifier, state_7.rx_data_1.repeat_count, state_7.rx_data_1.sticky_action, state_7.rx_data_1.action_mask, state_7.rx_data_1.goto_selector, state_7.rx_data_2_valid, state_7.rx_data_2.packet_type, state_7.rx_data_2.data.buffer_info(), state_7.rx_data_2.data_valid.buffer_info(), state_7.rx_data_2.err_match, state_7.rx_data_2.data_properties_valid, state_7.rx_data_2.data_properties.source_match_type, state_7.rx_data_2.data_properties.source_match_val, state_7.rx_data_2.data_properties.ep_match_type, state_7.rx_data_2.data_properties.ep_match_val, state_7.rx_data_2.data_properties.dev_match_type, state_7.rx_data_2.data_properties.dev_match_val, state_7.rx_data_2.data_properties.stream_id_match_type, state_7.rx_data_2.data_properties.stream_id_match_val, state_7.rx_data_2.data_properties.data_len_match_type, state_7.rx_data_2.data_properties.data_len_match_val, state_7.rx_data_2.match_modifier, state_7.rx_data_2.repeat_count, state_7.rx_data_2.sticky_action, state_7.rx_data_2.action_mask, state_7.rx_data_2.goto_selector, state_7.timer_valid, state_7.timer.timer_unit, state_7.timer.timer_val, state_7.timer.action_mask, state_7.timer.goto_selector, state_7.async_valid, state_7.async.event_type, state_7.async.edge_mask, state_7.async.repeat_count, state_7.async.sticky_action, state_7.async.action_mask, state_7.async.goto_selector, state_7.goto_0, state_7.goto_1, state_7.goto_2)
    # Call API function
    return api.py_bg_usb3_complex_match_config(beagle, validate, extout, c_state_0, c_state_1, c_state_2, c_state_3, c_state_4, c_state_5, c_state_6, c_state_7)


# Complex matching configuration for a single state
def bg_usb3_complex_match_config_single (beagle, validate, extout, state):
    """usage: int return = bg_usb3_complex_match_config_single(Beagle beagle, u08 validate, u08 extout, BeagleUsb3ComplexMatchState state)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # state pre-processing
    c_state = None
    if state != None:
        c_state = (state.tx_data_0_valid, state.tx_data_0.packet_type, state.tx_data_0.data.buffer_info(), state.tx_data_0.data_valid.buffer_info(), state.tx_data_0.err_match, state.tx_data_0.data_properties_valid, state.tx_data_0.data_properties.source_match_type, state.tx_data_0.data_properties.source_match_val, state.tx_data_0.data_properties.ep_match_type, state.tx_data_0.data_properties.ep_match_val, state.tx_data_0.data_properties.dev_match_type, state.tx_data_0.data_properties.dev_match_val, state.tx_data_0.data_properties.stream_id_match_type, state.tx_data_0.data_properties.stream_id_match_val, state.tx_data_0.data_properties.data_len_match_type, state.tx_data_0.data_properties.data_len_match_val, state.tx_data_0.match_modifier, state.tx_data_0.repeat_count, state.tx_data_0.sticky_action, state.tx_data_0.action_mask, state.tx_data_0.goto_selector, state.tx_data_1_valid, state.tx_data_1.packet_type, state.tx_data_1.data.buffer_info(), state.tx_data_1.data_valid.buffer_info(), state.tx_data_1.err_match, state.tx_data_1.data_properties_valid, state.tx_data_1.data_properties.source_match_type, state.tx_data_1.data_properties.source_match_val, state.tx_data_1.data_properties.ep_match_type, state.tx_data_1.data_properties.ep_match_val, state.tx_data_1.data_properties.dev_match_type, state.tx_data_1.data_properties.dev_match_val, state.tx_data_1.data_properties.stream_id_match_type, state.tx_data_1.data_properties.stream_id_match_val, state.tx_data_1.data_properties.data_len_match_type, state.tx_data_1.data_properties.data_len_match_val, state.tx_data_1.match_modifier, state.tx_data_1.repeat_count, state.tx_data_1.sticky_action, state.tx_data_1.action_mask, state.tx_data_1.goto_selector, state.tx_data_2_valid, state.tx_data_2.packet_type, state.tx_data_2.data.buffer_info(), state.tx_data_2.data_valid.buffer_info(), state.tx_data_2.err_match, state.tx_data_2.data_properties_valid, state.tx_data_2.data_properties.source_match_type, state.tx_data_2.data_properties.source_match_val, state.tx_data_2.data_properties.ep_match_type, state.tx_data_2.data_properties.ep_match_val, state.tx_data_2.data_properties.dev_match_type, state.tx_data_2.data_properties.dev_match_val, state.tx_data_2.data_properties.stream_id_match_type, state.tx_data_2.data_properties.stream_id_match_val, state.tx_data_2.data_properties.data_len_match_type, state.tx_data_2.data_properties.data_len_match_val, state.tx_data_2.match_modifier, state.tx_data_2.repeat_count, state.tx_data_2.sticky_action, state.tx_data_2.action_mask, state.tx_data_2.goto_selector, state.rx_data_0_valid, state.rx_data_0.packet_type, state.rx_data_0.data.buffer_info(), state.rx_data_0.data_valid.buffer_info(), state.rx_data_0.err_match, state.rx_data_0.data_properties_valid, state.rx_data_0.data_properties.source_match_type, state.rx_data_0.data_properties.source_match_val, state.rx_data_0.data_properties.ep_match_type, state.rx_data_0.data_properties.ep_match_val, state.rx_data_0.data_properties.dev_match_type, state.rx_data_0.data_properties.dev_match_val, state.rx_data_0.data_properties.stream_id_match_type, state.rx_data_0.data_properties.stream_id_match_val, state.rx_data_0.data_properties.data_len_match_type, state.rx_data_0.data_properties.data_len_match_val, state.rx_data_0.match_modifier, state.rx_data_0.repeat_count, state.rx_data_0.sticky_action, state.rx_data_0.action_mask, state.rx_data_0.goto_selector, state.rx_data_1_valid, state.rx_data_1.packet_type, state.rx_data_1.data.buffer_info(), state.rx_data_1.data_valid.buffer_info(), state.rx_data_1.err_match, state.rx_data_1.data_properties_valid, state.rx_data_1.data_properties.source_match_type, state.rx_data_1.data_properties.source_match_val, state.rx_data_1.data_properties.ep_match_type, state.rx_data_1.data_properties.ep_match_val, state.rx_data_1.data_properties.dev_match_type, state.rx_data_1.data_properties.dev_match_val, state.rx_data_1.data_properties.stream_id_match_type, state.rx_data_1.data_properties.stream_id_match_val, state.rx_data_1.data_properties.data_len_match_type, state.rx_data_1.data_properties.data_len_match_val, state.rx_data_1.match_modifier, state.rx_data_1.repeat_count, state.rx_data_1.sticky_action, state.rx_data_1.action_mask, state.rx_data_1.goto_selector, state.rx_data_2_valid, state.rx_data_2.packet_type, state.rx_data_2.data.buffer_info(), state.rx_data_2.data_valid.buffer_info(), state.rx_data_2.err_match, state.rx_data_2.data_properties_valid, state.rx_data_2.data_properties.source_match_type, state.rx_data_2.data_properties.source_match_val, state.rx_data_2.data_properties.ep_match_type, state.rx_data_2.data_properties.ep_match_val, state.rx_data_2.data_properties.dev_match_type, state.rx_data_2.data_properties.dev_match_val, state.rx_data_2.data_properties.stream_id_match_type, state.rx_data_2.data_properties.stream_id_match_val, state.rx_data_2.data_properties.data_len_match_type, state.rx_data_2.data_properties.data_len_match_val, state.rx_data_2.match_modifier, state.rx_data_2.repeat_count, state.rx_data_2.sticky_action, state.rx_data_2.action_mask, state.rx_data_2.goto_selector, state.timer_valid, state.timer.timer_unit, state.timer.timer_val, state.timer.action_mask, state.timer.goto_selector, state.async_valid, state.async.event_type, state.async.edge_mask, state.async.repeat_count, state.async.sticky_action, state.async.action_mask, state.async.goto_selector, state.goto_0, state.goto_1, state.goto_2)
    # Call API function
    return api.py_bg_usb3_complex_match_config_single(beagle, validate, extout, c_state)


# Extout configuration
def bg_usb3_ext_io_config (beagle, extin_enable, extout_modulation):
    """usage: int return = bg_usb3_ext_io_config(Beagle beagle, u08 extin_enable, BeagleUsbExtoutType extout_modulation)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_usb3_ext_io_config(beagle, extin_enable, extout_modulation)


# enum BeagleUsb3MemoryTestType
BG_USB3_MEMORY_TEST_FAST =  0
BG_USB3_MEMORY_TEST_FULL =  1
BG_USB3_MEMORY_TEST_SKIP = -1

def bg_usb3_memory_test (beagle, test):
    """usage: int return = bg_usb3_memory_test(Beagle beagle, BeagleUsb3MemoryTestType test)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_usb3_memory_test(beagle, test)


# Read functions
def bg_usb2_read (beagle, packet):
    """usage: (int return, u32 status, u32 events, u64 time_sop, u64 time_duration, u32 time_dataoffset, u08[] packet) = bg_usb2_read(Beagle beagle, u08[] packet)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function.

    Additionally, for arrays that are filled by the API function, an
    integer can be passed in place of the array argument and the API
    will automatically create an array of that length.  All output
    arrays, whether passed in or generated, are passed back in the
    returned tuple."""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # packet pre-processing
    __packet = isinstance(packet, int)
    if __packet:
        (packet, max_bytes) = (array_u08(packet), packet)
    else:
        (packet, max_bytes) = isinstance(packet, ArrayType) and (packet, len(packet)) or (packet[0], min(len(packet[0]), int(packet[1])))
        if packet.typecode != 'B':
            raise TypeError("type for 'packet' must be array('B')")
    # Call API function
    (_ret_, status, events, time_sop, time_duration, time_dataoffset) = api.py_bg_usb2_read(beagle, max_bytes, packet)
    # packet post-processing
    if __packet: del packet[max(0, min(_ret_, len(packet))):]
    return (_ret_, status, events, time_sop, time_duration, time_dataoffset, packet)


def bg_usb_read (beagle, packet, k_data):
    """usage: (int return, u32 status, u32 events, u64 time_sop, u64 time_duration, u32 time_dataoffset, BeagleUsbSource source, u08[] packet, u08[] k_data) = bg_usb_read(Beagle beagle, u08[] packet, u08[] k_data)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function.

    Additionally, for arrays that are filled by the API function, an
    integer can be passed in place of the array argument and the API
    will automatically create an array of that length.  All output
    arrays, whether passed in or generated, are passed back in the
    returned tuple."""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # packet pre-processing
    __packet = isinstance(packet, int)
    if __packet:
        (packet, max_bytes) = (array_u08(packet), packet)
    else:
        (packet, max_bytes) = isinstance(packet, ArrayType) and (packet, len(packet)) or (packet[0], min(len(packet[0]), int(packet[1])))
        if packet.typecode != 'B':
            raise TypeError("type for 'packet' must be array('B')")
    # k_data pre-processing
    __k_data = isinstance(k_data, int)
    if __k_data:
        (k_data, max_k_bytes) = (array_u08(k_data), k_data)
    else:
        (k_data, max_k_bytes) = isinstance(k_data, ArrayType) and (k_data, len(k_data)) or (k_data[0], min(len(k_data[0]), int(k_data[1])))
        if k_data.typecode != 'B':
            raise TypeError("type for 'k_data' must be array('B')")
    # Call API function
    (_ret_, status, events, time_sop, time_duration, time_dataoffset, source) = api.py_bg_usb_read(beagle, max_bytes, max_k_bytes, packet, k_data)
    # packet post-processing
    if __packet: del packet[max(0, min(_ret_, len(packet))):]
    # k_data post-processing
    if __k_data: del k_data[max(0, min(max_k_bytes, len(k_data))):]
    return (_ret_, status, events, time_sop, time_duration, time_dataoffset, source, packet, k_data)


# | return / 8
def bg_usb2_read_data_timing (beagle, packet, data_timing):
    """usage: (int return, u32 status, u32 events, u64 time_sop, u64 time_duration, u32 time_dataoffset, u08[] packet, u32[] data_timing) = bg_usb2_read_data_timing(Beagle beagle, u08[] packet, u32[] data_timing)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function.

    Additionally, for arrays that are filled by the API function, an
    integer can be passed in place of the array argument and the API
    will automatically create an array of that length.  All output
    arrays, whether passed in or generated, are passed back in the
    returned tuple."""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # packet pre-processing
    __packet = isinstance(packet, int)
    if __packet:
        (packet, max_bytes) = (array_u08(packet), packet)
    else:
        (packet, max_bytes) = isinstance(packet, ArrayType) and (packet, len(packet)) or (packet[0], min(len(packet[0]), int(packet[1])))
        if packet.typecode != 'B':
            raise TypeError("type for 'packet' must be array('B')")
    # data_timing pre-processing
    __data_timing = isinstance(data_timing, int)
    if __data_timing:
        (data_timing, max_timing) = (array_u32(data_timing), data_timing)
    else:
        (data_timing, max_timing) = isinstance(data_timing, ArrayType) and (data_timing, len(data_timing)) or (data_timing[0], min(len(data_timing[0]), int(data_timing[1])))
        if data_timing.typecode != 'I':
            raise TypeError("type for 'data_timing' must be array('I')")
    # Call API function
    (_ret_, status, events, time_sop, time_duration, time_dataoffset) = api.py_bg_usb2_read_data_timing(beagle, max_bytes, max_timing, packet, data_timing)
    # packet post-processing
    if __packet: del packet[max(0, min(_ret_, len(packet))):]
    # data_timing post-processing
    if __data_timing: del data_timing[max(0, min(_ret_, len(data_timing))):]
    return (_ret_, status, events, time_sop, time_duration, time_dataoffset, packet, data_timing)


def bg_usb2_read_bit_timing (beagle, packet, bit_timing):
    """usage: (int return, u32 status, u32 events, u64 time_sop, u64 time_duration, u32 time_dataoffset, u08[] packet, u32[] bit_timing) = bg_usb2_read_bit_timing(Beagle beagle, u08[] packet, u32[] bit_timing)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function.

    Additionally, for arrays that are filled by the API function, an
    integer can be passed in place of the array argument and the API
    will automatically create an array of that length.  All output
    arrays, whether passed in or generated, are passed back in the
    returned tuple."""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # packet pre-processing
    __packet = isinstance(packet, int)
    if __packet:
        (packet, max_bytes) = (array_u08(packet), packet)
    else:
        (packet, max_bytes) = isinstance(packet, ArrayType) and (packet, len(packet)) or (packet[0], min(len(packet[0]), int(packet[1])))
        if packet.typecode != 'B':
            raise TypeError("type for 'packet' must be array('B')")
    # bit_timing pre-processing
    __bit_timing = isinstance(bit_timing, int)
    if __bit_timing:
        (bit_timing, max_timing) = (array_u32(bit_timing), bit_timing)
    else:
        (bit_timing, max_timing) = isinstance(bit_timing, ArrayType) and (bit_timing, len(bit_timing)) or (bit_timing[0], min(len(bit_timing[0]), int(bit_timing[1])))
        if bit_timing.typecode != 'I':
            raise TypeError("type for 'bit_timing' must be array('I')")
    # Call API function
    (_ret_, status, events, time_sop, time_duration, time_dataoffset) = api.py_bg_usb2_read_bit_timing(beagle, max_bytes, max_timing, packet, bit_timing)
    # packet post-processing
    if __packet: del packet[max(0, min(_ret_, len(packet))):]
    # bit_timing post-processing
    if __bit_timing: del bit_timing[max(0, min(bg_bit_timing_size(BG_PROTOCOL_USB, _ret_), len(bit_timing))):]
    return (_ret_, status, events, time_sop, time_duration, time_dataoffset, packet, bit_timing)


def bg_usb2_reconstruct_timing (target_config, packet, bit_timing):
    """usage: (int return, u32[] bit_timing) = bg_usb2_reconstruct_timing(u32 target_config, u08[] packet, u32[] bit_timing)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function.

    Additionally, for arrays that are filled by the API function, an
    integer can be passed in place of the array argument and the API
    will automatically create an array of that length.  All output
    arrays, whether passed in or generated, are passed back in the
    returned tuple."""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # packet pre-processing
    (packet, num_bytes) = isinstance(packet, ArrayType) and (packet, len(packet)) or (packet[0], min(len(packet[0]), int(packet[1])))
    if packet.typecode != 'B':
        raise TypeError("type for 'packet' must be array('B')")
    # bit_timing pre-processing
    __bit_timing = isinstance(bit_timing, int)
    if __bit_timing:
        (bit_timing, max_timing) = (array_u32(bit_timing), bit_timing)
    else:
        (bit_timing, max_timing) = isinstance(bit_timing, ArrayType) and (bit_timing, len(bit_timing)) or (bit_timing[0], min(len(bit_timing[0]), int(bit_timing[1])))
        if bit_timing.typecode != 'I':
            raise TypeError("type for 'bit_timing' must be array('I')")
    # Call API function
    (_ret_) = api.py_bg_usb2_reconstruct_timing(target_config, num_bytes, packet, max_timing, bit_timing)
    # bit_timing post-processing
    if __bit_timing: del bit_timing[max(0, min(max_timing, len(bit_timing))):]
    return (_ret_, bit_timing)


# Hardware-based Statistics
class BeagleUsbStatsConfig:
    def __init__ (self):
        self.auto_config       = 0
        self.source_match_type = 0
        self.source_match_val  = 0
        self.ep_match_type     = 0
        self.ep_match_val      = 0
        self.dev_match_type    = 0
        self.dev_match_val     = 0

def bg_usb_stats_config (beagle, config):
    """usage: int return = bg_usb_stats_config(Beagle beagle, BeagleUsbStatsConfig config)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # config pre-processing
    c_config = None
    if config != None:
        c_config = (config.auto_config, config.source_match_type, config.source_match_val, config.ep_match_type, config.ep_match_val, config.dev_match_type, config.dev_match_val)
    # Call API function
    return api.py_bg_usb_stats_config(beagle, c_config)


def bg_usb_stats_config_query (beagle):
    """usage: (int return, BeagleUsbStatsConfig config) = bg_usb_stats_config_query(Beagle beagle)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    (_ret_, c_config) = api.py_bg_usb_stats_config_query(beagle)
    # config post-processing
    config = BeagleUsbStatsConfig()
    (config.auto_config, config.source_match_type, config.source_match_val, config.ep_match_type, config.ep_match_val, config.dev_match_type, config.dev_match_val) = c_config
    return (_ret_, config)


def bg_usb_stats_reset (beagle):
    """usage: int return = bg_usb_stats_reset(Beagle beagle)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_usb_stats_reset(beagle)


class BeagleUsb3GenStats:
    def __init__ (self):
        self.link                = 0
        self.lbad                = 0
        self.slc_crc5            = 0
        self.txn                 = 0
        self.lmp                 = 0
        self.lgo_u1              = 0
        self.lgo_u2              = 0
        self.lgo_u3              = 0
        self.dp                  = 0
        self.itp                 = 0
        self.shp_crc16_crc5      = 0
        self.sdp_crc32           = 0
        self.slc_frm_err         = 0
        self.shp_frm_err         = 0
        self.sdp_end_edb_frm_err = 0
        self.iso_ips             = 0
        self.para_ips            = 0
        self.carry_1k_dp         = 0

class BeagleUsb3ConnStats:
    def __init__ (self):
        self.txn         = 0
        self.dp          = 0
        self.ack         = 0
        self.nrdy        = 0
        self.erdy        = 0
        self.retry_ack   = 0
        self.carry_1k_dp = 0

class BeagleUsb2Stats:
    def __init__ (self):
        self.sof           = 0
        self.carry_1k_data = 0
        self.data          = 0
        self.bad_pid       = 0
        self.crc16         = 0
        self.crc5          = 0
        self.rx_error      = 0
        self.in_nak        = 0
        self.ping_nak      = 0

class BeagleUsbStats:
    def __init__ (self):
        self.usb3_tx_gen  = BeagleUsb3GenStats()
        self.usb3_rx_gen  = BeagleUsb3GenStats()
        self.usb3_tx_conn = BeagleUsb3ConnStats()
        self.usb3_rx_conn = BeagleUsb3ConnStats()
        self.usb2         = BeagleUsb2Stats()

def bg_usb_stats_read (beagle):
    """usage: (int return, BeagleUsbStats stats) = bg_usb_stats_read(Beagle beagle)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    (_ret_, c_stats) = api.py_bg_usb_stats_read(beagle)
    # stats post-processing
    stats = BeagleUsbStats()
    (stats.usb3_tx_gen.link, stats.usb3_tx_gen.lbad, stats.usb3_tx_gen.slc_crc5, stats.usb3_tx_gen.txn, stats.usb3_tx_gen.lmp, stats.usb3_tx_gen.lgo_u1, stats.usb3_tx_gen.lgo_u2, stats.usb3_tx_gen.lgo_u3, stats.usb3_tx_gen.dp, stats.usb3_tx_gen.itp, stats.usb3_tx_gen.shp_crc16_crc5, stats.usb3_tx_gen.sdp_crc32, stats.usb3_tx_gen.slc_frm_err, stats.usb3_tx_gen.shp_frm_err, stats.usb3_tx_gen.sdp_end_edb_frm_err, stats.usb3_tx_gen.iso_ips, stats.usb3_tx_gen.para_ips, stats.usb3_tx_gen.carry_1k_dp, stats.usb3_rx_gen.link, stats.usb3_rx_gen.lbad, stats.usb3_rx_gen.slc_crc5, stats.usb3_rx_gen.txn, stats.usb3_rx_gen.lmp, stats.usb3_rx_gen.lgo_u1, stats.usb3_rx_gen.lgo_u2, stats.usb3_rx_gen.lgo_u3, stats.usb3_rx_gen.dp, stats.usb3_rx_gen.itp, stats.usb3_rx_gen.shp_crc16_crc5, stats.usb3_rx_gen.sdp_crc32, stats.usb3_rx_gen.slc_frm_err, stats.usb3_rx_gen.shp_frm_err, stats.usb3_rx_gen.sdp_end_edb_frm_err, stats.usb3_rx_gen.iso_ips, stats.usb3_rx_gen.para_ips, stats.usb3_rx_gen.carry_1k_dp, stats.usb3_tx_conn.txn, stats.usb3_tx_conn.dp, stats.usb3_tx_conn.ack, stats.usb3_tx_conn.nrdy, stats.usb3_tx_conn.erdy, stats.usb3_tx_conn.retry_ack, stats.usb3_tx_conn.carry_1k_dp, stats.usb3_rx_conn.txn, stats.usb3_rx_conn.dp, stats.usb3_rx_conn.ack, stats.usb3_rx_conn.nrdy, stats.usb3_rx_conn.erdy, stats.usb3_rx_conn.retry_ack, stats.usb3_rx_conn.carry_1k_dp, stats.usb2.sof, stats.usb2.carry_1k_data, stats.usb2.data, stats.usb2.bad_pid, stats.usb2.crc16, stats.usb2.crc5, stats.usb2.rx_error, stats.usb2.in_nak, stats.usb2.ping_nak) = c_stats
    return (_ret_, stats)


def bg_usb2_stats_read (beagle):
    """usage: (int return, BeagleUsb2Stats stats) = bg_usb2_stats_read(Beagle beagle)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    (_ret_, c_stats) = api.py_bg_usb2_stats_read(beagle)
    # stats post-processing
    stats = BeagleUsb2Stats()
    (stats.sof, stats.carry_1k_data, stats.data, stats.bad_pid, stats.crc16, stats.crc5, stats.rx_error, stats.in_nak, stats.ping_nak) = c_stats
    return (_ret_, stats)



#==========================================================================
# USB 480 API
#==========================================================================
# General constants
BG480_TRUNCATION_LENGTH = 4
BG480V2_USB2_BUFFER_SIZE_256MB = 256

#==========================================================================
# USB 5000 API
#==========================================================================
# General constants
BG5000_USB2_BUFFER_SIZE_128MB = 128
BG5000_USB3_BUFFER_SIZE_2GB = 2
BG5000_USB3_BUFFER_SIZE_4GB = 4
# Cross-Analyzer Sync Configuration
# enum Beagle5000CrossAnalyzerSyncMode
BG5000_CROSS_ANALYZER_SYNC_WAIT   = 0
BG5000_CROSS_ANALYZER_SYNC_BYPASS = 1

# enum Beagle5000CrossAnalyzerMode
BG5000_CROSS_ANALYZER_ACCEPT = 0
BG5000_CROSS_ANALYZER_IGNORE = 1

def bg5000_cross_analyzer_sync_config (beagle, cross_sync_mode, cross_trigger_mode, cross_stop_mode):
    """usage: int return = bg5000_cross_analyzer_sync_config(Beagle beagle, Beagle5000CrossAnalyzerSyncMode cross_sync_mode, Beagle5000CrossAnalyzerMode cross_trigger_mode, Beagle5000CrossAnalyzerMode cross_stop_mode)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg5000_cross_analyzer_sync_config(beagle, cross_sync_mode, cross_trigger_mode, cross_stop_mode)


def bg5000_cross_analyzer_sync_release (beagle):
    """usage: int return = bg5000_cross_analyzer_sync_release(Beagle beagle)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg5000_cross_analyzer_sync_release(beagle)



#==========================================================================
# MDIO API
#==========================================================================
# enum BeagleMdioClause
BG_MDIO_CLAUSE_22    = 0
BG_MDIO_CLAUSE_45    = 1
BG_MDIO_CLAUSE_ERROR = 2

BG_MDIO_OPCODE22_WRITE = 0x01
BG_MDIO_OPCODE22_READ = 0x02
BG_MDIO_OPCODE22_ERROR = 0xff
BG_MDIO_OPCODE45_ADDR = 0x00
BG_MDIO_OPCODE45_WRITE = 0x01
BG_MDIO_OPCODE45_READ_POSTINC = 0x02
BG_MDIO_OPCODE45_READ = 0x03
# Read the next MDIO frame.
def bg_mdio_read (beagle):
    """usage: (int return, u32 status, u64 time_sop, u64 time_duration, u32 time_dataoffset, u32 data_in) = bg_mdio_read(Beagle beagle)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_mdio_read(beagle)


def bg_mdio_read_bit_timing (beagle, bit_timing):
    """usage: (int return, u32 status, u64 time_sop, u64 time_duration, u32 time_dataoffset, u32 data_in, u32[] bit_timing) = bg_mdio_read_bit_timing(Beagle beagle, u32[] bit_timing)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function.

    Additionally, for arrays that are filled by the API function, an
    integer can be passed in place of the array argument and the API
    will automatically create an array of that length.  All output
    arrays, whether passed in or generated, are passed back in the
    returned tuple."""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # bit_timing pre-processing
    __bit_timing = isinstance(bit_timing, int)
    if __bit_timing:
        (bit_timing, max_timing) = (array_u32(bit_timing), bit_timing)
    else:
        (bit_timing, max_timing) = isinstance(bit_timing, ArrayType) and (bit_timing, len(bit_timing)) or (bit_timing[0], min(len(bit_timing[0]), int(bit_timing[1])))
        if bit_timing.typecode != 'I':
            raise TypeError("type for 'bit_timing' must be array('I')")
    # Call API function
    (_ret_, status, time_sop, time_duration, time_dataoffset, data_in) = api.py_bg_mdio_read_bit_timing(beagle, max_timing, bit_timing)
    # bit_timing post-processing
    if __bit_timing: del bit_timing[max(0, min(bg_bit_timing_size(BG_PROTOCOL_MDIO, _ret_), len(bit_timing))):]
    return (_ret_, status, time_sop, time_duration, time_dataoffset, data_in, bit_timing)


# Parse the raw MDIO data into the standard format.
# This function will fill the supplied fields as per
# the constants defined above.  If the raw data contains
# a malformed turnaround field, the caller will be
# notified of the error through the return value of
# this function (BG_MDIO_BAD_TURNAROUND).
def bg_mdio_parse (packet):
    """usage: (int return, u08 clause, u08 opcode, u08 addr1, u08 addr2, u16 data) = bg_mdio_parse(u32 packet)"""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_bg_mdio_parse(packet)



#==========================================================================
# IV MON API
#==========================================================================
# Extract the current and voltage values in the packet returned by
# bg_usb_read().
def bg_iv_mon_parse (packet):
    """usage: (int return, f32 voltage, f32 current) = bg_iv_mon_parse(u08[] packet)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function."""

    if not BG_LIBRARY_LOADED: return BG_INCOMPATIBLE_LIBRARY
    # packet pre-processing
    (packet, length) = isinstance(packet, ArrayType) and (packet, len(packet)) or (packet[0], min(len(packet[0]), int(packet[1])))
    if packet.typecode != 'B':
        raise TypeError("type for 'packet' must be array('B')")
    # Call API function
    return api.py_bg_iv_mon_parse(length, packet)


