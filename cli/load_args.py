import sys
import logging

from util import exceptions, validate

from .globl import globl


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
        globl.extensions.clear()
        globl.extensions.append(r'.*\..*(?!\/)')

    # Descargar archivos
    if '-d' in sys.argv:
        globl.args['download'] = True

    # Ser recursivo
    if '-r' in sys.argv:
        globl.args['recursive'] = True
        globl.extensions.append('/')

    # Ser verboso
    if '-v' in sys.argv or len(sys.argv) <= 1:
        globl.args['verbose'] = True
        logging.basicConfig(
            format="%(message)s",
            level=logging.INFO)

    # Ser Java!! :O
    if '-vv' in sys.argv:
        globl.args['verbose'] = True
        logging.basicConfig(
            format="%(levelname)s\t-\t( %(filename)s -> %(funcName)s:%(lineno)d )\t-\t%(message)s",
            level=logging.DEBUG)

    # Definir una plantilla
    if '-t' in sys.argv:
        try:
            globl.args['template'] = sys.argv[sys.argv.index('-t') + 1]
            if globl.args['template'].startswith('-'):
                raise exceptions.BadParameterException('-t needs one argument')
        except exceptions.BadParameterException:
            help_message('-t')

    # Definir argumento de salida
    if '-o' in sys.argv:
        try:
            globl.args['output'] = sys.argv[sys.argv.index('-o') + 1]
            if globl.args['output'].startswith('-'):
                raise exceptions.BadParameterException('-o needs one argument')
        except exceptions.BadParameterException:
            help_message('-o')
        if not globl.args.get('template'):
            globl.args['template'] = 'txt'
        with open(globl.args['output'], 'w+', encoding='utf-8') as f:
            if globl.args.get('template') == 'm3u':
                f.write('#EXTM3U\n')

    # Cargar links desde la linea de parametros
    for arg in sys.argv:
        if arg.startswith('-') or not validate.https(arg):
            continue  # Si el argumento no se ajusta a la sintaxis de https ignorarlo
        globl.LINKS.append(arg)
        logging.info('[%s] loaded!', arg)
