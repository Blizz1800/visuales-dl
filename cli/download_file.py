from tqdm import tqdm
from urllib.parse import unquote
from os import path, makedirs
import logging

from .get_stream import main as get_stream
from .globl import fileList


def main(fList: list):
    """Download file into corresponding directory"""
    indexes = []
    for index in fList:
        if index in indexes:
            logging.debug('Saltando indice: %d', index)
            continue  # Si ya hemos descargado este indice nos lo saltamos
        indexes.append(index)
        try:
            url = fileList[index].get('url')
            element = fileList[index].get('name')
            fSize = fileList[index].get('fsize')
            subfolder = fileList[index].get('subfolder')
            basefolder = fileList[index].get('basefolder')
            stream, size = get_stream(url)  # Obtenemos el stream del archivo
            block_size = 1024
            # Definimos la carpeta donde se va a escribir en caso de recursion
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
            # Ruta absolua al archivo
            out_file = path.join(folder, unquote(element))
            print(f"{index+1}. {element} | [{fSize}] -> {out_file}")
            # En caso de la descarga del archivo no haya terminado
            if not path.exists(out_file) or path.getsize(out_file) < size:
                # Escribimos el archivo
                with open(out_file, 'wb') as dFile:
                    for data in tqdm(stream.iter_content(block_size),
                                     desc=element, unit_divisor=1024,
                                     total=size//block_size, unit='b',
                                     unit_scale=True):
                        dFile.write(data)
            print("Complete!\n")
        except KeyboardInterrupt:
            with open(path.join('.', 'index.txt'), 'w+') as f:
                if not f.writable:
                    break
                f.write(str(index+1))
            return
