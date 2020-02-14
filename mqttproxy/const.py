"""Constants used by MQTT proxy for Home Assistant components."""
MAJOR_VERSION = 0
MINOR_VERSION = 1
PATCH_VERSION = "2.alpha"
__short_version__ = "{}.{}".format(MAJOR_VERSION, MINOR_VERSION)
__version__ = "{}.{}".format(__short_version__, PATCH_VERSION)
__language__ = "en"
REQUIRED_PYTHON_VER = (3, 7, 0)
# Truthy date string triggers showing related deprecation warning messages.
REQUIRED_NEXT_PYTHON_VER = (3, 8, 0)
REQUIRED_NEXT_PYTHON_DATE = ""

# Format for platform files
PLATFORM_FORMAT = "{platform}.{domain}"
# #### API / REMOTE ####
SERVER_PORT = 8080

URL_ROOT = "/"
URL_API = "/api/"

ALL_PROXIES_TOPIC='allmqttproxies'

# The exit code to send to request a restart
RESTART_EXIT_CODE = 100
