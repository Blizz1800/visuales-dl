import requests
import logging
import re
from urllib.parse import unquote

from .globl import WEB_SITE, VISITED, args, extensions, base_folder
from .add_file_to_list import main as add_file_to_list
from .write_list import main as write_list


def main(link: str, subfolder: str = ''):
    # Definimos el directorio padre para no regresar a el
    parent = '/'.join(link.split('/')[0:-2]) + '/'
    global base_folder
    if not base_folder and not subfolder:
        # Ajustamos la carpeta padre en caso de recursion
        base_folder = unquote(link.split('/')[-2])
    logging.debug("base_folder[%s] subfolder[%s]", base_folder, subfolder)
    data = requests.get(link, timeout=10000)
    if data.status_code != 200:
        logging.error('[%d] Error occurred with [%s]!', data.status_code, link)
    # Obtenemos todos todas las etiquetas <a> de la pagina
    for element in re.findall('<a href="(.*)">.*</a>', data.text):
        for ext in extensions:
            # Verificamos q el elemento capturado no comiense con '?'
            if re.match(fr'^(?!\?).*\.?{ext}$', element):
                url = f"{WEB_SITE}{element}"
                if not element.startswith('/'):
                    url = f"{link}{element}"
                if args.get('recursive', False) and (url == parent or url in VISITED):
                    continue  # Verificamos que intentamos buscar una recursion y el link no ha sido visitado ni es el padre
                VISITED.append(url)  # Agregamos la URL a las web visitadas
                if element.endswith('/'):  # Entramos al link hijo en caso de recursion
                    subfolder = unquote(url.split('/')[-2])
                    main(url, subfolder)
                    continue
                if not args.get('download'):  # Si no vamos a descargar los archivos
                    if args.get('output'):
                        logging.info(url)
                        write_list(url, element, ext) # Escribimos la lista como se debe
                    elif not args.get('output') and not args.get('verbose'):
                        print(url) # Sino escribimos en la salida estandar
                    else:
                        logging.info(url)
                else:
                    add_file_to_list(url, base_folder, subfolder)
