import logging
from .globl import globl
from .add_file_to_list import add_file_to_list
from .write_list import write_list


def process_file(url, element, ext, subfolder):
    if globl.args.get('download'):
        add_file_to_list(url, globl.base_folder, subfolder)
        return
    if globl.args.get('output'):
        logging.info(url)
        # Escribimos la lista como se debe
        write_list(url, element, ext)
    elif not globl.args.get('output') and not globl.args.get('verbose'):
        print(url)  # Sino escribimos en la salida estandar
    else:
        logging.info(url)
