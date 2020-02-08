#!/usr/bin/env python3

from bluepy.btle import Scanner, DefaultDelegate

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, is_new_dev, is_new_data):
        if is_new_dev:
            print("Discovered device {}".format(dev.addr))
        elif is_new_data:
            print("Received new data from {}".format(dev.addr))

def scan()->[]:
    scanner = Scanner().withDelegate(ScanDelegate())
    devices = scanner.scan(10.0)

    for dev in devices:
        print("Device {} ({}), RSSI={} dB".format(dev.addr, dev.addrType, dev.rssi))
        for (adtype, desc, value) in dev.getScanData():
            print("  {} = {}".format(desc, value))
