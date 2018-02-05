# UART Bluetooth Logger using Saleae Logic Analyzers

## Hardware Setup

Connect the probes as follows:
- Digital Channel 0: Bluetooth TX
- Digital Channel 1: Bluetooth RX
- Digital Channel 2: Console UART TX - optionally

If Digital Channel 2 is connected to the Console UART, line-delimited messages will be integrated into the .pklg file. Not implemented yet.

## How to use it

Capture a trace of the Bluetooth communication in the Logic app as usual. Then, use the "Export Data" menu to save the data into a file using the following settings:
- Digital Only
- Channels 0, 1, 2 (if console UART used)
- All samples
- CSV

After saving, do

	$ ./process_trace.py filename.csv

It will create filename.pklg in the current dircetory.

## Future Work
- Inline console UART from Channel 2
- Oversampling of logic trace
- Switch to .vcd format instead of .csv
- Follow baud rate changes by decoding "HCI Local Information Event" and then detecting proprietary baud rate change commands




