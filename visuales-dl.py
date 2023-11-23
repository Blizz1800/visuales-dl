import requests
import re 
import logging
from sys import argv
from os import path, mkdir
from urllib.parse import unquote
from tqdm import tqdm
from pprint import pprint

# Global Variables
args = {}
extensions = ["avi", "srt", "mkv", "mpg", "mp4"]
base_url = ""
fileList = []

# Display Help Message and exit
def help(onError=''):
    if onError:
        print(f"\nError: {onError} needs one argument!")
    help_dict = [{
        'flag': '-a',
        'desc': "Detect all elements"
    },{
        'flag': '-d',
        'desc': "Download elements"
    },{
        'flag': '-v',
        'desc': "Be verbose"
    },{
        'flag': '-vv',
        'desc': "Be MORE verbose!!"
    },{
        'flag': '-t <arg>',
        'desc': "Especify a template type (valid 'txt' and 'm3u')"
    },{
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
    exit()


# Loads arguments from the cli
def loadArgs():
    if '-h' in argv:
        help()
    
    if '-a' in argv:
        extensions.append('.*')

    if '-d' in argv:
        args['download'] = True

    if '-v' in argv:
        args['verbose'] = True
        logging.basicConfig(format="%(levelname)s\t-\t[ %(asctime)s ]\t-\t( %(funcName)s )\t-\t%(message)s", level=logging.INFO)

    if '-vv' in argv or len(argv) <= 1:
        args['verbose'] = True
        logging.basicConfig(format="%(levelname)s\t-\t[ %(asctime)s ]\t-\t( %(funcName)s )\t-\t%(message)s", level=logging.DEBUG)
        
    if '-t' in argv:
        try:
            args['template'] = argv[argv.index('-t') + 1]
            if args['template'].startswith('-'):
                raise Exception('-t needs one argument')
        except:
            help('-t')
            
    if '-o' in argv:
        try:
            args['output'] = argv[argv.index('-o') + 1]
            if args['output'].startswith('-'):
                    raise Exception('-o needs one argument')
        except:
            help('-o')
        if not args.get('template'):
            args['template'] = 'txt'
        f = open(args['output'], 'w+')
        if args.get('template') == 'm3u':
            f.write('#EXTM3U\n')
        f.close()


def getStream(url):
    stream = requests.get(url, stream=True)
    size = int(stream.headers.get('content-length', 0))
    return (stream, size)


def addFileToList(url):
    stream, size = getStream(url)
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
    logging.info(f"Load [{file_url}] ({size})")
    fileList.append({
        'name': unquote(file_url),
        'url' : url,
        'size': size,
        'fsize': f"{nSize}{unit}",
    })
    

# Download file into corresponding directory
def downloadFile(fList: list):
    global base_url
    global fileList
    for index in fList:
        try: 
            url = fileList[index-1].get('url')
            element = fileList[index-1].get('name')
            fSize = fileList[index-1].get('fsize')
            stream, size = getStream(url)
            block_size = 1024
            i = -1
            while base_url.split('/')[i] == '':
                i -= 1
            folder = path.join('.', unquote(base_url.split('/')[i])) 
            if not path.exists(folder):
                mkdir(folder)
            out_file = path.join(folder, unquote(element))
            print(f"{index}. {element} | [{fSize}]")
            with open(out_file, 'wb') as dFile:
                logging.info(f'{out_file} [{size}]')
                for data in tqdm(stream.iter_content(block_size), total=size//block_size, unit='KB', unit_scale=True):
                    dFile.write(data)
            print("Complete!\n")
        except KeyboardInterrupt:
            return

# Write links in format of M3U
def writeM3U(output, url, ext, element):
    if ext == 'srt':
            return
    slave = re.sub(f'(.*\.){ext}$', '\g<1>srt', url)
    output.write(f"#EXTINF:0,{element}\n#EXTVLCOPT:input-slave={slave}\n#EXTVLCOPT:network-caching=1000\n{url}\n")


# Write links in format of TXT (link/line)
def writeTXT(output, url):
    output.write(url + '\n')


# Define what kind of file list should to use
def writeList(url: str, element: str, ext: str):
    out = open(args['output'], 'a+')
    if args.get('template') == 'txt':
        writeTXT(out, url)
    if args.get('template') == 'm3u':
        writeM3U(out, url, ext, element)
    out.close()


# Start the GUI
def gui():
    pass


# Initiate the CLI
def cli():
    global base_url
    base_url = input('Introduzca la URL de la web: ')
    data = requests.get(base_url)
    for element in re.findall('<a href="(.*)">.*</a>', data.text):
        for ext in extensions:
            if (re.match(f'^.*\.{ext}$', element)):
                url = f"{base_url}{element}"
                if not args.get('download'):
                    if args.get('output') and not args.get('verbose'):
                       writeList(url, element, ext)
                    elif args.get('output') and args.get('verbose'):
                        with open(args['output'], 'a+') as out:
                            out.write(url + '\r\n')
                        logging.info(url)
                    else:
                        logging.info(url)
                else:
                    addFileToList(url)
    if args.get('download'):
        print()
        downloadList = []
        for i, e in enumerate(fileList):
            print(f"{i}. {e.get('name')} [{e.get('fsize')}]")
        print()
        print("a\tTodos\nX-Y\tFrom X to Y\nX,Y,Z\tDownload X, Y and Z\nA-F,L-T,Z\tDownload from A to F, from L to T, and Z\ne\tShow examples\nc\tCancel Download\n")
        while True:
            selection = input("Choose what files you wanna download: ")
            if 'e' in selection:
                print('7-10\tDownload 7, 8, 9, 10\n7,9\tDownload 7 and 9\n7-9,23\tDownload 7, 8, 9 and 23')
                continue
            elif 'a' in selection:
                downloadList = [e.get('url') for e in fileList]
                break
            downloadList = selection.split(',')
            for i, e in enumerate(downloadList):
                if '-' in e:
                    t = e.split('-')
                    downloadList[i] = [index for index in range(int(t[0]), int(t[1])+1)]
                else:
                    downloadList[i] = [int(e)]
            break
        for i in downloadList:
            if downloadList.index(i) > 0:
                for o in i:
                    downloadList[0].append(o)
                downloadList.remove(i)
        downloadList = downloadList[0]
        downloadFile(downloadList)


# Entry point
if __name__ == '__main__':
    loadArgs()
    if args.get('GUI'):
        gui()
    else:
        cli()
        
