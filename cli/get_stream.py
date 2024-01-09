import requests


def main(url):
    """returns the stream and size in Bytes"""
    size = 0
    tries = 0
    while size == 0 and tries < 3:  # Comprobamos q no hallan errores al cargar el size del archivo
        stream = requests.get(url, stream=True, timeout=10000)
        size = int(stream.headers.get('content-length', 0))
    return (stream, size)
