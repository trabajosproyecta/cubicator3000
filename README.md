# Cubicator3000

El cubicator3000 es una aplicación para optimizar los cortes de las construcciones de
 proyecta y desplegar el resultado a través de una visualización amigable que puede ir directo al manual.
 Actualmente esta disponible en versión web (Flask) y versión de escritorio (tkinter).

Gracias a @JoseAlamos por la idea y versión original y a [@shgoldfarb](https://github.com/SHGoldfarb) (2016-1)  por la
versión 2.0 con cplex.

## Aplicación de escritorio

[Ver acá](app/cubicator/README.md)

## Aplicación Web

La aplicación web consiste en una simple aplicación flask y una sóla vista HTML/CSS practicamente estática.
Cada vez que se llama al cubicador se generan archivos temporales que se eliminan una vez creado el zip final.

El manejo de errores no esta implementado.


### Desarrollo
La instalación y desarrollo de la aplicación es mediante un contenedor de docker y docker-compose (basado en [esto](https://github.com/tiangolo/uwsgi-nginx-flask-docker)). Por lo que basta 
tener instaladas ambas herramientas para hacer funcionar todo. Para comenzar clonar el repositorio y dentro de la carpeta:

```bash
sudo docker-compose build
```
Con eso se descargan todas las dependencias (incluyendo python). Luego para montar la aplicación:

```bash
sudo docker-compose up
```
Y podrás ver la aplicación en localhost.

### Dependencias

Las dependencias se manejan mediante docker y pip, por lo que para agregar una debes ponerla en el archivo 
`requirements.txt` dentro de la carpeta `app`.

### Diseño

Dentro de la carpeta `app` se encuentra todo, `cubicator` corresponde al módulo de optimización, `main.py` es la 
aplicación flask y en `temp` se guardan los archivos temporales. El resto de las carpetas sigue las convenciones tradicionales
de flask.

## Deployment

Para deployar la aplicación basta montar el servidor con docker como se explica arriba ya que el contenedor ya incluye la
 instalación y configuración de Nginx. (con el flag `-d` queda corriendo como daemon.)

## Colaboradores

 * Hielo [@ironcadiz](https://github.com/ironcadiz)
 * Sam [@shgoldfarb](https://github.com/SHGoldfarb)
