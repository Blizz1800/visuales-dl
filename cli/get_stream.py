from .send_request import send_request


def get_stream(url):
    """returns the stream and size in Bytes"""
    size = 0
    tries = 0
    while size == 0 and tries < 3:  # Comprobamos q no hallan errores al cargar el size del archivo
        stream = send_request(url, True)
        size = int(stream.headers.get('content-length', 0))
    return (stream, size)
