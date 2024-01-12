import requests
from requests.exceptions import ReadTimeout
import logging

from .globl import config


def send_request(url, stream=False):
    tryies = config.getint('requests', 'retry_per_link')
    for i in range(tryies+1):
        try:
            data = requests.get(url, stream=stream, timeout=config.getint('requests', 'timeout'))
            break
        except ReadTimeout:
            if i < tryies:
                if logging.getLogger().level >= 10:
                    print('Timeout error, retrying... {}'.format(i+1), end='\n')
                continue
            logging.error('Timeout error, not possible to load %s', url)
            exit()
    return data
