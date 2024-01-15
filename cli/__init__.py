from .process_link import process_link
from .download_file import download_file
from .load_args import load_args
from .globl import globl
from .load_download import load_download

from util import validate

import logging
from urllib.parse import unquote


def cli():
    """Initiate the CLI"""
    # Si no detectamos links desde la linea de comandos
    if not len(globl.LINKS):
        globl.LINKS.extend(input('Introduzca la URL de la web: ').split(' '))
    # Comenzamos a iterar todos los links
    for url in globl.LINKS:
        if not validate.https(url):
            logging.info("\"%s\" no es una url valida!", unquote(url))
            continue
        # La base de la url para obtener el nombre de dominio
        globl.WEB_SITE = '/'.join(url.split('/')[0:3])
        logging.debug("Processing: %s [%s]", url, globl.WEB_SITE)
        # Revisamos si el link seleccionado ya esta en cache'
        data = globl.db.select('downloads', where={
            'url': url
        })
        # Si la informacion de descarga no existe
        if not data:
            globl.download_id = globl.db.insert('downloads', {
                'name': globl.base_folder,
                'url': url
            })
            process_link(url)
        else:
            load_download(data)
            continue
        globl.db.update(
            'downloads', {
                'complete': 1,
            }, {
                'id': globl.download_id,
                'complete': 0
            })
    # Si hay archivos en la lista, comenzamos el proceso de
    # descarga en kso de q este sea requerido
    if globl.args.get('download') and len(globl.fileList):
        print()
        download_list = []
        lastGroup = ''
        # Mostramos la lista de archivos
        for i, e in enumerate(globl.fileList):
            if e.get('subfolder') != lastGroup:
                if i:
                    print()
                print(e.get('subfolder'))
                lastGroup = e.get('subfolder')
            print(f"{i+1}. {e.get('name')} [{e.get('fsize')}{e.get('unit')}]")
        print()
        print("a\t\tTodos\nX-Y\t\tFrom X to Y\nX,Y,Z\t\tDownload X, Y and Z\nA-F,L-T,Z\tDownload from A to F, from L to T, and Z\ne\t\tShow examples\nc\t\tCancel Download\n")
        while True:
            selection = input(
                "Choose what files you wanna download: ").replace(' ', '')
            if 'e' in selection:
                print(
                    '7-10\tDownload 7, 8, 9, 10\n7,9\tDownload 7 and 9\n7-9,23\tDownload 7, 8, 9 and 23')
                continue
            elif 'a' in selection:
                # Agregamos a la lista de descarga todos los indices (ints) de la lista d archivos
                download_list = list(range(1, len(globl.fileList)+1))
                break
            download_list = selection.split(',')
            for e in download_list:
                # Ajusta siempre al primer elemento de la lista
                e = download_list[0]
                del download_list[0]  # Lo elimina de la lista
                if not type(e) is str:
                    break  # Si no es un string, significa que terminamos y salimos
                try:
                    if '-' in e:
                        t = e.split('-')
                        # Agregamos todos los valores entre desde A hasta B tal q ("A - B")
                        l = list(range(
                            # Menor de ambos
                            min(len(globl.fileList)-1, min(
                                int(t[0]), int(t[1]))) - 1,
                            # Mayor de ambos
                            min(len(globl.fileList)-1, max(
                                int(t[0]), int(t[1]))) + 1
                        ))
                        # En ambos casos seleccionamos el minimo entre el resultado
                        # y el total de elementos de la lista para evitar un overbound
                        download_list.extend(l)
                    else:
                        download_list.append(int(e)-1)
                except ValueError:
                    logging.debug('%s no es un int', e)
                    continue
            break
        logging.debug('Has seleccionado: %s', download_list)
        download_file(download_list)
