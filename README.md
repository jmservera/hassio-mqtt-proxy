# hassio-mqtt-proxy

![Python application](https://github.com/jmservera/hassio-mqtt-proxy/workflows/Python%20application/badge.svg?branch=master)

> Warning! this project is in the first phase of development and is not functional at all 

A simple mqtt proxy to send data to Home Assistant. It creates a device for marking the proxy as enabled when running. It has been greatly inspired by the [miflora mqtt daemon](https://github.com/ThomDietrich/miflora-mqtt-daemon) but also contains auto discovery and device integration to know when the Raspi was down or unstable. It's specifically designed for [Home Assistant](https://github.com/home-assistant).

We are using virtual environment, to develop do:

```bash
 sudo apt-get update && \
 sudo apt-get install -y python3.7 python3-pip libglib2.0-dev bluez

 python3 -m venv venv 
 source venv/bin/activate
 pip install -r requirements.txt
```

## Device discovery

Discovery feature needs the service to be run under elevated privileges. If you don't have elevation it will not work.
