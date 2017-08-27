# Cubicator3000

El cubicator3000 es una aplicación de escritorio (hasta ahora) para optimizar los cortes de las construcciones de
 proyecta y desplegar el resultado a través de una visualización amigable que puede ir directo al manual.
 
Gracias a @JoseAlamos por la idea y versión original y a [@shgoldfarb](https://github.com/SHGoldfarb) (2016-1)  por la 
versión 2.0 con cplex.
 
## Dependencias versión 3.0 (branch development):

* xlrd 
* xlwt 
* Pillow-PIL
* numpy
* pulp


## Procedimiento de desarrollo.

 La branch principal de desarrollo es `development`. Todo trabajo debe llevarse o hacerse en ella antes de pasarse a 
 `master`.
  
 Recuerda desarrollar en un virtualenv de python y no en la instalación nativa, es una buena práctica y facilitará el 
 paso a `.exe` o a ejecutable
 
 Recuerda también no programar en espanglish siempre que sea posible. El código legado ya esta en espanglish y 
 probablemente nunca nadie lo arregle. 

## Objetivos de esta versión (3.0 /3000):

* Deshacerse de ampl para simplificar el uso e instalación.

* Generar una GUI amigable para que cualquier jefe futuro no computín / no ingeniero pueda instalar el programa en 
cualquier plataforma y usarlo fácilmente.

* Crear interfaz para agregar construcciones nuevas.

* Hacer refactoring profundo del código para que sea mantenible por cualquier jefe / comisionado que desee trabajar en el.
 
## Diseño del sistema
El programa esta dividido en 4 archivos:

* `main.py` es el archivo legado de la versión anterior y es el que se ejecuta.
* `excel_handler.py` contiene las funciones para abrir y guardar los archivos `.xlsx`.
* `drawer.py` contiene las funciones para crear las imágenes.
* `optimizer.py` contiene funciones constructoras del modelo usando la libreria pulp.


## Contribuyentes
 
 * Hielo ([@ironcadiz](https://github.com/ironcadiz)) 
 