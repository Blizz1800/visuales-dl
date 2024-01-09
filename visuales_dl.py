from cli import load_args, args, cli
from gui import gui


# Entry point
if __name__ == '__main__':
    load_args()
    if args.get('GUI'):
        gui()
    else:
        cli()
