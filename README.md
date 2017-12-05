# Cubicator3000

El cubicator3000 es una aplicación de escritorio (hasta ahora) para optimizar los cortes de las construcciones de
 proyecta y desplegar el resultado a través de una visualización amigable que puede ir directo al manual.

Gracias a @JoseAlamos por la idea y versión original y a [@shgoldfarb](https://github.com/SHGoldfarb) (2016-1)  por la
versión 2.0 con cplex.

## Dependencias versión 3.0:

* xlrd
* xlwt
* Pillow-PIL
* numpy
* pulp


## Procedimiento de desarrollo.

 Recuerda desarrollar en un virtualenv de python y no en la instalación nativa, es una buena práctica y facilitará el
 paso a `.exe` o a ejecutable

 Recuerda también no programar en espanglish siempre que sea posible. El código legado ya esta en espanglish y
 probablemente nunca nadie lo arregle.

## Objetivos de esta versión (3.0 /3000):

* Deshacerse de ampl para simplificar el uso e instalación.

* Generar una GUI amigable para que cualquier jefe futuro no computín / no ingeniero pueda instalar el programa en
cualquier plataforma y usarlo fácilmente.

* Hacer refactoring profundo del código para que sea mantenible por cualquier jefe / comisionado que desee trabajar en el.

## Diseño del sistema
El programa esta dividido en 4 archivos:

* `backend.py` archivo legado de la versión anterior. contiene la función principal y genera el output.
* `excel_handler.py` contiene las funciones para abrir y guardar los archivos `.xlsx`.
* `drawer.py` contiene las funciones para crear las imágenes.
* `optimizer.py` contiene funciones constructoras del modelo usando la libreria pulp.
* `cubicator3000` es una interfaz gráfica simple para dar el archivo de input y directorios de output.

## Sobre el optimizador
El algoritmo de optimización corresponde a resolver un problema simple de programación lineal entera lo que se logra a través de
la librería pulp. Los solvers de pulp no estan hechos en python si no que son ejecutables dentro de la librería, lo que genera que
estos no sean reconocidos al pasar a un ejecutable con `pyinstaller`. La solución es  copiar el solver desde la librería pulp
manualmente a  la misma carpeta donde esta el código. los solvers se encuentran en `path_virtualenv/lib/python3.5/site-packages/pulp/solverdir/cbc`
Para finalmente decirle a pulp que debe usar el solver desde el archivo descargado ( de esta manera al crear el ejecutable nos basta decirle a
`pyinstaller` que copie los archivos o podemos hacerlo a mano). Esto esta implementado en la función `solve()` de el
archivo `optimizer.py`, donde se debe dejar la línea del sistema operativo en que estés trabajando descomentada.


## Generar ejecutable
Para generar un ejecutable debes instalar la librería `pyinstaller` en tu virtualenv y luego ejecutar en la carpeta cubicator el comando:
```bash
pyinstaller --noconsole cubicator3000.py
```
Eso generará la carpeta `dist` con el ejecutable. Luego debes copiar el archivo `arial.ttf` y
la carpeta con el solver a `dist/cubicator3000/`. Finalmente agrega el manual y el excel de prueba a la carpeta `dist/`.

## Colaboradores

 * Hielo [@ironcadiz](https://github.com/ironcadiz)
 * Sam [@shgoldfarb](https://github.com/SHGoldfarb)
