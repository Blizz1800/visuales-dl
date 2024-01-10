from cli import load_args, globl, cli
from gui import gui


# Entry point
if __name__ == '__main__':
    load_args()
    if globl.args.get('GUI'):
        gui()
    else:
        cli()
