"""Downloader for the https://visuales.uclv.cu/ web"""
# pylint: disable=global-variable-not-assigned, global-statement, too-many-branches, invalid-name, no-else-continue
import re
import logging
from sys import argv
import sys
from os import path, makedirs
from urllib.parse import unquote
from tqdm import tqdm
import requests

# Utils
from util import exceptions

# Global Variables
args = {}
extensions = ["avi", "srt", "mkv", "mpg", "mp4"]
LINKS = []
WEB_SITE = ""
VISITED = []
fileList = []


def help_message(on_error=''):
    """Display Help Message and exit

    Args:
        on_error (str, optional): Show the error message. Defaults to ''.
    """

    if on_error:
        print(f"\nError: {on_error} needs one argument!")
    help_dict = [{
        'flag': '-a',
        'desc': "Detect all elements"
    }, {
        'flag': '-d',
        'desc': "Download elements"
    }, {
        'flag': '-v',
        'desc': "Be verbose"
    }, {
        'flag': '-vv',
        'desc': "Be MORE verbose!!"
    }, {
        'flag': '-t <arg>',
        'desc': "Especify a template type (valid 'txt' and 'm3u')"
    }, {
        'flag': '-o <arg>',
        'desc': "Especify the output template file"
    }]
    print()
    for h in help_dict:
        if len(h.get('flag')) < 7:
            print(f"{h.get('flag')}\t\t{h.get('desc')}")
            continue
        print(f"{h.get('flag')}\t{h.get('desc')}")
    print()
    sys.exit()


# Loads arguments from the cli
def load_args():
    """Loads args"""
    if '-h' in argv:
        help_message()

    if '-a' in argv:
        extensions.clear()
        extensions.append('.*')

    if '-d' in argv:
        args['download'] = True

    if '-r' in argv:
        args['recursive'] = True
        extensions.append('/')

    if '-v' in argv:
        args['verbose'] = True
        logging.basicConfig(
            format="%(levelname)s\t-\t[ %(asctime)s ]\t-\t( %(funcName)s:%(lineno)d )\t-\t%(message)s",
            level=logging.INFO)

    if '-vv' in argv or len(argv) <= 1:
        args['verbose'] = True
        logging.basicConfig(
            format="%(levelname)s\t-\t[ %(asctime)s ]\t-\t( %(funcName)s:%(lineno)d )\t-\t%(message)s",
            level=logging.DEBUG)

    if '-t' in argv:
        try:
            args['template'] = argv[argv.index('-t') + 1]
            if args['template'].startswith('-'):
                raise exceptions.BadParameterException('-t needs one argument')
        except exceptions.BadParameterException:
            help_message('-t')

    if '-o' in argv:
        try:
            args['output'] = argv[argv.index('-o') + 1]
            if args['output'].startswith('-'):
                raise exceptions.BadParameterException('-o needs one argument')
        except exceptions.BadParameterException:
            help_message('-o')
        if not args.get('template'):
            args['template'] = 'txt'
        with open(args['output'], 'w+', encoding='utf-8') as f:
            if args.get('template') == 'm3u':
                f.write('#EXTM3U\n')
    for arg in argv:
        if arg.startswith('-') or not re.match(r'\bhttps?:\/\/[\w\-+&@#\/%=~|$?_\!*\'()\[\],.;:]+', arg):
            continue
        LINKS.append(arg)
        logging.info('[%s] loaded!', arg)


def get_stream(url):
    """returns the stream and size in Bytes"""
    stream = requests.get(url, stream=True, timeout=10000)
    size = int(stream.headers.get('content-length', 0))
    return (stream, size)


def add_file_to_list(url: str, basefolder='', subfolder: str = ''):
    """Add file to download list"""
    stream, size = get_stream(url)
    stream.close()
    nSize = size
    file_url = url.split('/')[-1]
    UNITS = ['B', 'KB', 'MB', 'GB']
    unit = UNITS[0]
    for i, u in enumerate(UNITS):
        if size // 1024 ** i > 0:
            nSize = size // 1024 ** i
            unit = u
            continue
        break
    if not file_url:
        return
    if subfolder:
        logging.info("From [%s] load [%s] (%s)", subfolder,
                     unquote(file_url), f"{nSize}{unit}")
    else:
        logging.info("Load [%s] (%s)", unquote(file_url), f"{nSize}{unit}")
    fileList.append({
        'name': unquote(file_url),
        'url': url,
        'size': size,
        'fsize': f"{nSize}{unit}",
        'unit': unit,
        'subfolder': subfolder,
        'basefolder': basefolder,
    })


def download_file(fList: list):
    """Download file into corresponding directory"""
    global fileList
    for index in fList:
        try:
            url = fileList[index-1].get('url')
            element = fileList[index-1].get('name')
            fSize = fileList[index-1].get('fsize')
            subfolder = fileList[index-1].get('subfolder')
            basefolder = fileList[index-1].get('basefolder')
            stream, size = get_stream(url)
            block_size = 1024
            i = -1
            while not basefolder.split('/')[i]:
                i -= 1
            folder = path.join('.', 'download', unquote(
                basefolder.split('/')[i]).replace(':', '_'))
            subfolder = path.join(folder, subfolder)
            if not path.exists(folder):
                makedirs(folder)
            if subfolder:
                if not path.exists(subfolder):
                    makedirs(subfolder)
                folder = subfolder
            out_file = path.join(folder, unquote(element))
            print(f"{index}. {element} | [{fSize}] -> {out_file}")
            with open(out_file, 'wb') as dFile:
                for data in tqdm(stream.iter_content(block_size),
                                 desc=element, unit_divisor=1204,
                                 total=size//block_size, unit='b',
                                 unit_scale=True):
                    dFile.write(data)
            print("Complete!\n")
        except KeyboardInterrupt:
            return


def write_m3u(output, url, ext, element):
    """Write links in format of M3U"""
    if ext == 'srt':
        return
    slave = re.sub(fr'(.*\.){ext}$', r'\g<1>srt', url)
    output.write(f"""#EXTINF:0,{element}
#EXTVLCOPT:input-slave={slave}
#EXTVLCOPT:network-caching=1000
{url}
""")


def write_txt(output, url):
    """Write links in format of TXT (link/line)"""
    output.write(url + '\n')


def write_list(url: str, element: str, ext: str):
    """Define what kind of file list should to use"""
    with open(args['output'], 'a+', encoding='utf-8') as out:
        if args.get('template') == 'txt':
            write_txt(out, url)
        if args.get('template') == 'm3u':
            write_m3u(out, url, ext, element)


def gui():
    """Start the GUI"""


def process_link(link: str, subfolder: str = ''):
    parent = '/'.join(link.split('/')[0:-2]) + '/'
    data = requests.get(link, timeout=10000)
    if data.status_code != 200:
        logging.error('[%d] Error occurred with [%s]!', data.status_code, link)
    for element in re.findall('<a href="(.*)">.*</a>', data.text):
        for ext in extensions:
            if re.match(fr'^(?!\?).*\.?{ext}$', element):
                url = f"{WEB_SITE}{element}"
                if not element.startswith('/'):
                    url = f"{link}{element}"
                if args.get('recursive', False) and (url == parent or url in VISITED):
                    continue
                VISITED.append(url)
                if element.endswith('/'):
                    subfolder = unquote(url.split('/')[-2])
                    process_link(url, subfolder)
                    continue
                if not args.get('download'):
                    if args.get('output') and not args.get('verbose'):
                        write_list(url, element, ext)
                    elif args.get('output') and args.get('verbose'):
                        with open(args['output'], 'a+', encoding='utf-8') as out:
                            out.write(url + '\r\n')
                        logging.info(url)
                    else:
                        logging.info(url)
                else:
                    add_file_to_list(url, link, subfolder)


def cli():
    """Initiate the CLI"""
    global WEB_SITE
    global VISITED
    global LINKS
    if not len(LINKS):
        LINKS.append(input('Introduzca la URL de la web: '))
    for url in LINKS:
        WEB_SITE = '/'.join(url.split('/')[0:3])
        process_link(url)
    if args.get('download') and len(fileList):
        print()
        download_list = []
        # fileList.sort(key=lambda k: k.get('size'))
        lastGroup = ''
        for i, e in enumerate(fileList):
            if e.get('subfolder') != lastGroup:
                if i:
                    print()
                print(e.get('subfolder'))
                lastGroup = e.get('subfolder')
            print(f"{i+1}. {e.get('name')} [{e.get('fsize')}]")
        print()
        print("""a\tTodos
X-Y\tFrom X to Y
X,Y,Z\tDownload X, Y and Z
A-F,L-T,Z\tDownload from A to F, from L to T, and Z
e\tShow examples
c\tCancel Download
""")
        while True:
            selection = input("Choose what files you wanna download: ")
            if 'e' in selection:
                print('''7-10\tDownload 7, 8, 9, 10
7,9\tDownload 7 and 9
7-9,23\tDownload 7, 8, 9 and 23''')
                continue
            elif 'a' in selection:
                # download_list = [e.get('url') for e in fileList]
                download_list = list(range(len(fileList)))
                download_list = [download_list]
                break
            download_list = selection.split(',')
            for i, e in enumerate(download_list):
                if '-' in e:
                    t = e.split('-')
                    # download_list[i] = [index for index in range(int(t[0]), int(t[1])+1)]
                    download_list[i] = list(range(int(t[0]), int(t[1])+1))
                else:
                    download_list[i] = [int(e)]
            break
        for i in download_list:
            if download_list.index(i) > 0:
                for o in i:
                    download_list[0].append(o)
                download_list.remove(i)
        download_list = download_list[0]
        download_file(download_list)


# Entry point
if __name__ == '__main__':
    load_args()
    if args.get('GUI'):
        gui()
    else:
        cli()
