# USB Bluetooth Logger using TotalPhase Beagle USB Protocol Analyzers

## Hardware Setup

Plug the USB Bluetooth Controller into the Beagle as usual and connect it to your host.

## How to use it

	./capture_bluetooth_usb.py

It will capture HCI traffic and save it to hci_dump.pklg in the current directory.
Press Control-C to stop capturing. 

## How to analyzer packet log

The resulting file can be analyzed with Wireshark or the Apple's PacketLogger tool.

## Heuristic to avoid re-enumeration on start

To correctly identify the endpoints, you usually unplug and replug the USB device to trigger an enumeration by the host. To avoid this for our use case, we employ the following heuristic:
- HCI Commands are sent as a USB Control Transfer and an USB Control Transfer is preceeded by a SETUP packet. We identify the endpoint of the first SETUP packet as the endpoint for the HCI Commands.
- We assume all OUT packets that are not on the Control endpoint to be outgoing ACL packets.
- ACL packets can only be received after a connection has been established, therefore we assume that there will be at least one HCI Event before any HCI ACL packets. We then wait until the Control endpoint is identified and use the first IN packet that is not for the Control endpoint as the Interrupt endpoint for HCI Events. 
- We assume that IN packets that are not on the Interrupt endoint to be incoming ACL packets.




