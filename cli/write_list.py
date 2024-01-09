from .globl import args
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


def main(url: str, element: str, ext: str):
    """Define what kind of file list should to use"""
    with open(args['output'], 'a+', encoding='utf-8') as out:
        if args.get('template', 'txt') == 'txt':  # Verificamos q la plantilla sea txt
            write_txt(out, url)
        elif args.get('template') == 'm3u': # Verificamos q la plantilla sea m3u
            write_m3u(out, url, ext, element) 
