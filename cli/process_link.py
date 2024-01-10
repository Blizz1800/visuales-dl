import requests
import logging
import re
from urllib.parse import unquote

from .globl import globl
from .add_file_to_list import main as add_file_to_list
from .write_list import main as write_list


def main(link: str, subfolder: str = ''):
    # Definimos el directorio padre para no regresar a el
    parent = '/'.join(link.split('/')[0:-2]) + '/'
    if not globl.base_folder and not subfolder:
        # Ajustamos la carpeta padre en caso de recursion
        globl.base_folder = unquote(link.split('/')[-2])
    logging.debug("web[%s] base_folder[%s] subfolder[%s] parent[%s]",
                  globl.WEB_SITE, globl.base_folder, subfolder, parent)
    data = requests.get(link, timeout=10000)
    if data.status_code != 200:
        logging.error('[%d] Error occurred with [%s]!', data.status_code, link)
    # Obtenemos todos todas las etiquetas <a> de la pagina
    for element in re.findall('<a href="(.*)">.*</a>', data.text):
        for ext in globl.extensions:
            # Verificamos q el elemento capturado no comiense con '?'
            if re.match(fr'^(?!\?).*\.?{ext}$', element):
                url = f"{globl.WEB_SITE}{element}"
                if not element.startswith('/'):
                    url = f"{link}{element}"
                if globl.args.get('recursive', False) and (url == parent or url in globl.VISITED):
                    continue  # Verificamos que intentamos buscar una recursion y el link no ha sido visitado ni es el padre
                logging.debug("%s is not parent [%s]", url, parent)
                # Agregamos la URL a las web visitadas
                globl.VISITED.append(url)
                if element.endswith('/'):  # Entramos al link hijo en caso de recursion
                    subfolder = unquote(url.split('/')[-2])
                    main(url, subfolder)
                    continue
                # Si no vamos a descargar los archivos
                if not globl.args.get('download'):
                    if globl.args.get('output'):
                        logging.info(url)
                        # Escribimos la lista como se debe
                        write_list(url, element, ext)
                    elif not globl.args.get('output') and not globl.args.get('verbose'):
                        print(url)  # Sino escribimos en la salida estandar
                    else:
                        logging.info(url)
                else:
                    add_file_to_list(url, globl.base_folder, subfolder)
