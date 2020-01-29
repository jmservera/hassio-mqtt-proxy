# hassio-mqtt-proxy

A simple mqtt proxy to send data to Home Assistant. It creates a device for marking the proxy as enabled when running.

We are using virtual environment, to develop do:

```bash
 sudo apt-get update && \
 sudo apt-get install -y python3.7 python3-pip libglib2.0-dev bluez
 
 python3 -m venv venv 
 source venv/bin/activate
 pip install -r requirements.txt
```
