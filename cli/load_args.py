import sys
import logging
import re

from util import exceptions

from .globl import args, extensions, LINKS


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


def main():
    """Loads args"""
    if '-h' in sys.argv:
        help_message()

    # Detectar todas las posibles extensiones de archivo
    if '-a' in sys.argv:
        extensions.clear()
        extensions.append('.*')

    # Descargar archivos 
    if '-d' in sys.argv:
        args['download'] = True

    # Ser recursivo
    if '-r' in sys.argv:
        args['recursive'] = True
        extensions.append('/')

    # Ser muy verboso 
    if '-v' in sys.argv:
        args['verbose'] = True
        logging.basicConfig(
            format="%(levelname)s\t-\t[ %(asctime)s ]\t-\t( %(funcName)s:%(lineno)d )\t-\t%(message)s",
            level=logging.INFO)
    
    # Ser Java!! :O
    if '-vv' in sys.argv or len(sys.argv) <= 1:
        args['verbose'] = True
        logging.basicConfig(
            format="%(levelname)s\t-\t[ %(asctime)s ]\t-\t( %(filename)s.%(funcName)s:%(lineno)d )\t-\t%(message)s",
            level=logging.DEBUG)

    # Definir una plantilla
    if '-t' in sys.argv:
        try:
            args['template'] = sys.argv[sys.argv.index('-t') + 1]
            if args['template'].startswith('-'):
                raise exceptions.BadParameterException('-t needs one argument')
        except exceptions.BadParameterException:
            help_message('-t')

    # Definir argumento de salida
    if '-o' in sys.argv:
        try:
            args['output'] = sys.argv[sys.argv.index('-o') + 1]
            if args['output'].startswith('-'):
                raise exceptions.BadParameterException('-o needs one argument')
        except exceptions.BadParameterException:
            help_message('-o')
        if not args.get('template'):
            args['template'] = 'txt'
        with open(args['output'], 'w+', encoding='utf-8') as f:
            if args.get('template') == 'm3u':
                f.write('#EXTM3U\n')
    
    # Cargar links desde la linea de parametros
    for arg in sys.argv:
        if arg.startswith('-') or not re.match(r'\bhttps?:\/\/[\w\-+&@#\/%=~|$?_\!*\'()\[\],.;:]+', arg):
            continue # Si el argumento no se ajusta a la sintaxis de https ignorarlo
        LINKS.append(arg)
        logging.info('[%s] loaded!', arg)
