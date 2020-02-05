#!/usr/bin/env python3
"""mqtt proxy setup script."""
from datetime import datetime as dt

from setuptools import find_packages, setup

import mqttproxy.const as mqttproxy_const

PROJECT_NAME = "MQTT Proxy for Home Assistant"
PROJECT_PACKAGE_NAME = "mqttproxy"
PROJECT_LICENSE = "MIT License"
PROJECT_AUTHOR = "Servezas"
PROJECT_COPYRIGHT = " 2020-{}, {}".format(dt.now().year, PROJECT_AUTHOR)
PROJECT_URL = "https://servezas.io/"
PROJECT_EMAIL = "hello@servezas.io"

PROJECT_GITHUB_USERNAME = "jmservera"
PROJECT_GITHUB_REPOSITORY = "hassio-mqtt-proxy"

PYPI_URL = "https://pypi.python.org/pypi/{}".format(PROJECT_PACKAGE_NAME)
GITHUB_PATH = "{}/{}".format(PROJECT_GITHUB_USERNAME, PROJECT_GITHUB_REPOSITORY)
GITHUB_URL = "https://github.com/{}".format(GITHUB_PATH)

DOWNLOAD_URL = "{}/archive/{}.zip".format(GITHUB_URL, mqttproxy_const.__version__)
PROJECT_URLS = {
    "Bug Reports": "{}/issues".format(GITHUB_URL),
    "Dev Docs": "https://developers.servezas.io/",
    "Discord": "https://discordapp.com/invite/noinvitebynow"
}

PACKAGES = find_packages(exclude=["tests", "tests.*"])

REQUIRES = [
"miflora==0.6",
"wheel==0.33.6",
"paho-mqtt==1.4.0",
"flask==1.1.1",
"colorama==0.4.3",
"Unidecode==1.1.1",
"bluepy==1.3.0",
"PyYAML==5.3",
"munch==2.5.0",
"waitress==1.4.2"
]

MIN_PY_VERSION = ".".join(map(str, mqttproxy_const.REQUIRED_PYTHON_VER))

setup(
    name=PROJECT_PACKAGE_NAME,
    version=mqttproxy_const.__version__,
    url=PROJECT_URL,
    download_url=DOWNLOAD_URL,
    project_urls=PROJECT_URLS,
    author=PROJECT_AUTHOR,
    author_email=PROJECT_EMAIL,
    packages=PACKAGES,
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIRES,
    python_requires=">={}".format(MIN_PY_VERSION),
    test_suite="test",
    entry_points={"console_scripts": ["mqttproxy = mqttproxy.__main__:main"]},
)
