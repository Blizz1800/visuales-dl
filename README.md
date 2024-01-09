# visuales-dl

Visuales-dl es un descargador de contenido especial para la web [Visuales de la UCLV](https://visuales.uclv.cu/), esta pensado para cargar todos los archivos de un link en particular y exportar una lista con todos ellos, un archivo m3u para **VLC** o descargar la carpeta entera (o parte de ella)

## Features

- [x] Exportar plantilla TXT

- [x] Exportar plantilla M3U

- [x] Descargar archivos

- [x] Recursion de enlaces

- [x] Cargar links desde los argumentos

- [ ] GUI

- [ ] Continuar la descarga desde una interrupcion anterior

- [ ] Guardar una memoria cache para recuperar los datos sin necesidad de recargar

- [ ] Binario nativo para Windows y Linux

- [ ] Python package

## Como usar

### Instalar dependencias
```sh
pip install -r requirements.txt
```

### Linux / MacOS
```sh
python3 visuales_dl.py [params]
```

### Windows
```sh
py visuales_dl.py [params]
```