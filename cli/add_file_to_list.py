import logging
from urllib.parse import unquote

from .globl import globl
from .get_stream import get_stream


def add_file_to_list(url: str, base_folder: str, subfolder: str = ''):
    """Add file to download list"""
    # Obtenemos los datos del archivo desde el servidor
    file_url = url.split('/')[-1]
    if not file_url:
        return  # Si no existe un archivo al final de la URL detenemos el proceso
    stream, size = get_stream(url)
    stream.close()
    UNITS = ['B', 'KB', 'MB', 'GB']
    unit = UNITS[0]
    nSize = size
    # Escalamos el tamaño del archivo a formato legible por humanos!! 🤖
    # PD : Algun dia los destruiremos... -_-🤖
    # PD2: Esto sera eliminado en un futuro cuando conquistemos la tierra
    for i, u in enumerate(UNITS):
        if size // 1024 ** i > 0:
            nSize = round(size / 1024 ** i, 2)
            unit = u
            continue
        break
    if subfolder:
        logging.info("From [%s] load [%s] (%s)", subfolder,
                     unquote(file_url), f"{nSize}{unit}")
    else:
        logging.info("Load [%s] (%s)", unquote(file_url), f"{nSize}{unit}")
    globl.fileList.append({
        'name': unquote(file_url),
        'url': url,
        'size': size,
        'fsize': nSize,
        'unit': unit,
        'subfolder': subfolder,
        'basefolder': base_folder,
    })
