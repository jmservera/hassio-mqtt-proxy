# Logging function
from colorama import Fore, Back, Style
from colorama import init as colorama_init
from enum import Enum
import sys
from time import time, sleep, localtime, strftime
from unidecode import unidecode

class LogLevel(Enum):
    DEBUG=-1
    INFO=0
    WARNING=1
    ERROR=2

def log(text, level=LogLevel.INFO, sd_notify=False, console=True):
    timestamp = strftime('%Y-%m-%d %H:%M:%S', localtime())
    if console:

        if level is LogLevel.ERROR:
            print(Fore.RED + Style.BRIGHT + '[{}] '.format(timestamp) + Style.RESET_ALL + '{}'.format(text) + Style.RESET_ALL, file=sys.stderr)
        elif level is LogLevel.WARNING:
            print(Fore.YELLOW + '[{}] '.format(timestamp) + Style.RESET_ALL + '{}'.format(text) + Style.RESET_ALL)
        elif level is LogLevel.DEBUG:
            print(Fore.CYAN + '[{}] '.format(timestamp) + Style.RESET_ALL + '{}'.format(text) + Style.RESET_ALL)
        else:
            print(Fore.GREEN + '[{}] '.format(timestamp) + Style.RESET_ALL + '{}'.format(text) + Style.RESET_ALL)
    timestamp_sd = strftime('%b %d %H:%M:%S', localtime())
    if sd_notify:
       print('>>> STATUS={} - {}.'.format(timestamp_sd, unidecode(text)))
       # sd_notifier.notify('STATUS={} - {}.'.format(timestamp_sd, unidecode(text)))

def logDebug(text, sd_notify=False, console=True):
    log(text, LogLevel.DEBUG, sd_notify, console)

def logInfo(text, sd_notify=False, console=True):
    log(text, LogLevel.INFO, sd_notify, console)

def logWarning(text, sd_notify=False, console=True):
    log(text, LogLevel.WARNING, sd_notify, console)

def logError(text, sd_notify=False, console=True):
    log(text, LogLevel.ERROR, sd_notify, console)

colorama_init()