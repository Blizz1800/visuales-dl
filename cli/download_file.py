from tqdm import tqdm
from urllib.parse import unquote
from os import path, makedirs
import logging

from .get_stream import get_stream
from .globl import globl


def get_file(index):
    url = globl.fileList[index].get('url')
    name = globl.fileList[index].get('name')
    fSize = globl.fileList[index].get('fsize')
    unit = globl.fileList[index].get('unit')
    subfolder = globl.fileList[index].get('subfolder')
    basefolder = globl.fileList[index].get('basefolder')
    return (url, name, fSize, unit, subfolder, basefolder)


def get_folder(basefolder, subfolder):
    folder = path.join('.', 'download', unquote(basefolder))
    # Definimos la subcarpeta correspondiente de cada archivo en
    # caso de recursion o la carpeta donde se va a almacenar
    subfolder = path.join(folder, subfolder)
    if not path.exists(folder):
        makedirs(folder)
    if subfolder:
        if not path.exists(subfolder):
            makedirs(subfolder)
        folder = subfolder
    return folder


def download_file(fList: list):
    """Download file into corresponding directory"""
    indexes = []
    block_size = 1024
    for index in fList:
        if index in indexes:
            logging.debug('Saltando indice: %d', index)
            continue  # Si ya hemos descargado este indice nos lo saltamos
        indexes.append(index)
        index -= 1
        url, name, fSize, unit, subfolder, basefolder = get_file(index)
        # Definimos la carpeta donde se va a escribir en caso de recursion
        folder = get_folder(basefolder, subfolder)
        # Ruta absolua al archivo
        out_file = path.join(folder, unquote(name))
        # En caso de la descarga del archivo no haya terminado
        print(f"{index+1}. {name} | [{fSize}{unit}] -> {out_file}")
        while True:
            # Obtenemos el stream del archivo
            try:
                stream, size = get_stream(url, 10000)
            except KeyboardInterrupt:
                return
            pbar = tqdm(total=size, unit_divisor=1024,
                        leave=False, unit='B',
                        unit_scale=True, dynamic_ncols=True)
            try:
                if not path.exists(out_file) or path.getsize(out_file) < size or not globl.db.select('files', where={'url': url, 'complete': 1}):
                    # Escribimos el archivo
                    with open(out_file, 'wb') as dFile:
                        pbar.clear()
                        for block in stream.iter_content(block_size):
                            if block:
                                pbar.update(len(block))
                                dFile.write(block)
                        pbar.close()
                pbar.clear()
                pbar.close()
                print("Complete!\n")
                globl.db.update('files', {
                    'complete': 1,
                }, {
                    'url': url,
                    'complete': 0
                })
                break
            except Exception as e:
                pbar.clear()
                pbar.close()
                if logging.getLogger().level <= logging.ERROR:
                    print("\rHa ocurrido un error, reintentando...", end='')
                    print(e)
                with open(path.join('.', 'index.txt'), 'w+') as f:
                    if not f.writable:
                        return
                    f.write(str(index+1))
                continue
