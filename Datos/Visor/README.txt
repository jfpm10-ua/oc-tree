Instrucciones para compilar el visualizador desde línea de comandos:

Debemos tener instalada la Point Cloud Library (paquete libpcl-dev en ubuntu)

Desde el directorio donde se ha descomprimido el visor:

$ mkdir build
$ cd build
$ cmake ..

Si cmake termina con todo ok (si no, resolver las dependencias)

$ make
