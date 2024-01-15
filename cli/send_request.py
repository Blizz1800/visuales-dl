import requests
from requests.exceptions import ReadTimeout, ConnectionError
import logging

from .globl import config


def send_request(url, stream=False, timeout=None):
    tryies = config.getint('requests', 'retry_per_link')
    for i in range(tryies+1):
        try:
            data = requests.get(url, stream=stream, timeout=timeout if timeout else config.getint('requests', 'timeout'))
            break
        except (ReadTimeout, ConnectionError):
            if i < tryies:
                print('\rTimeout error, retrying... {}\r'.format(i+1), end='')
                continue
            logging.error('Timeout error, not possible to load %s', url)
            exit()
    return data
