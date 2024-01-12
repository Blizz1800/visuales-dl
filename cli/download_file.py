from tqdm import tqdm
from urllib.parse import unquote
from os import path, makedirs
import logging

from .get_stream import main as get_stream
from .globl import globl


def main(fList: list):
    """Download file into corresponding directory"""
    indexes = []
    for index in fList:
        if index in indexes:
            logging.debug('Saltando indice: %d', index)
            continue  # Si ya hemos descargado este indice nos lo saltamos
        indexes.append(index)
        try:
            url = globl.fileList[index].get('url')
            element = globl.fileList[index].get('name')
            fSize = globl.fileList[index].get('fsize')
            subfolder = globl.fileList[index].get('subfolder')
            basefolder = globl.fileList[index].get('basefolder')
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
                    pbar = tqdm(desc=element, total=size,
                                unit_divisor=1024, leave=False,
                                unit='B', unit_scale=True)
                    pbar.clear()
                    for block in stream.iter_content(block_size):
                        if block:
                            pbar.update(len(block))
                            dFile.write(block)
                    pbar.close()
            print("Complete!\n")
        except KeyboardInterrupt:
            with open(path.join('.', 'index.txt'), 'w+') as f:
                if not f.writable:
                    break
                f.write(str(index+1))
            return
