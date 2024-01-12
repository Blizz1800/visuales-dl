from .globl import globl
import re


def write_m3u(output, url, ext, element):
    """Write links in format of M3U"""
    if ext == 'srt':
        return
    slave = re.sub(fr'(.*\.){ext}$', r'\g<1>srt', url)
    output.write(
        f"#EXTINF:0,{element}\n#EXTVLCOPT:input-slave={slave}\n#EXTVLCOPT:network-caching=1000\n{url}\n")


def write_txt(output, url):
    """Write links in format of TXT (link/line)"""
    output.write(url + '\n')


def write_list(url: str, element: str, ext: str):
    """Define what kind of file list should to use"""
    with open(globl.args['output'], 'a+', encoding='utf-8') as out:
        # Verificamos q la plantilla sea txt
        if globl.args.get('template', 'txt') == 'txt':
            write_txt(out, url)
        # Verificamos q la plantilla sea m3u
        elif globl.args.get('template') == 'm3u':
            write_m3u(out, url, ext, element)
