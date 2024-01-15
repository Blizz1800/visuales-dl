from .globl import globl
from .process_link import process_link

import re


def load_download(data):
    '''Si la descarga esta cargada por completo, cargamos 
    directamente los archivos en base de datos'''
    globl.download_id = data[0]
    if data[-1]:  # Complete
        files_id = globl.db.select('files_downloads', ['file_id'], where={
            'download_id': globl.download_id})
        for i in files_id:
            i = i[0]
            file = globl.db.select(
                'files',
                ['name', 'url', 'size',
                    'fsize', 'unit', 'subfolder',
                    'basefolder'], {
                    'id': i,
                    'complete': 0
                })
            if not file:
                continue
            name, url, size, nSize, unit, subfolder, base_folder = file
            for ext in globl.extensions:
                if not re.search(ext, name):
                    continue
                json_file = {
                    'name': name,
                    'url': url,
                    'size': size,
                    'fsize': nSize,
                    'unit': unit,
                    'subfolder': subfolder,
                    'basefolder': base_folder,
                }
                globl.fileList.append(json_file)
                break
    else:
        process_link(data[2]) # URL 
