import logging
from urllib.parse import unquote

from .globl import globl
from .get_stream import get_stream


def add_file_to_list(url: str, base_folder: str, subfolder: str = ''):
    """Add file to download list"""
    # Obtenemos los datos del archivo desde el servidor
    file_name = url.split('/')[-1]
    if not file_name:
        return  # Si no existe un archivo al final de la URL detenemos el proceso
    file = globl.db.select('files', where={
        'url': url
    }, many=1)
    if not file:
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
    else:
        size, nSize, unit, subfolder, base_folder, completed = tuple(file[3:])
        if completed:
            return

    if subfolder:
        logging.info("From [%s] load [%s] (%s)", subfolder,
                     unquote(file_name), f"{nSize}{unit}")
    else:
        logging.info("Load [%s] (%s)", unquote(file_name), f"{nSize}{unit}")
    data = {
        'name': unquote(file_name),
        'url': url,
        'size': size,
        'fsize': nSize,
        'unit': unit,
        'subfolder': subfolder,
        'basefolder': base_folder,
    }
    globl.fileList.append(data)
    if not file:
        file_id = globl.db.insert('files', data)
        globl.db.insert('files_downloads', {
            'file_id': file_id,
            'download_id': globl.download_id
        })
