#!/usr/bin/env python3

from bluepy.btle import Scanner, DefaultDelegate
from threading import Thread, Semaphore
import asyncio
import errno


class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, is_new_dev, is_new_data):
        if is_new_dev:
            print("Discovered device {}".format(dev.addr))
        elif is_new_data:
            print("Received new data from {}".format(dev.addr))

_semaphore=Semaphore()

def scan(timeout=10.0)->[]:
    if(_semaphore.acquire(True,0.5)):
        try:
            scanner = Scanner().withDelegate(ScanDelegate())
            devices = scanner.scan(timeout)

            for dev in devices:
                print("Device {} ({}), RSSI={} dB".format(dev.addr, dev.addrType, dev.rssi))
                for (adtype, desc, value) in dev.getScanData():
                    print("  {} = {}".format(desc, value))
            return devices
        except Exception as ex:
            log_error('Error {}'.format(ex))
        finally:
            _semaphore.release()
    else:
        raise BlockingIOError(errno.EINPROGRESS)    

async def scan_async(timeout=10.0)->[]:
    loop=asyncio.get_running_loop()
    return await loop.run_in_executor(None,scan,timeout)