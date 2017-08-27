from PIL import Image, ImageDraw, ImageFont
import os

TTF = "arial.ttf"
ANCHO = 2


def crea_rectangulo(draw, xyxy, ancho, fill=(255, 255, 255)):
    for i in range(ancho):
        draw.rectangle([x - i for x in xyxy], outline=(0, 0, 0), fill=fill)


def centrar_texto(draw, xyxy, texto):
    x0, y0, x1, y1 = xyxy
    tamanio = int(min(max((x1 - x0) / 8 + 10, 5), 40))
    draw.text(
        [max(x0, (x0 + x1) / 2 - len(texto) * tamanio * 0.35),
         (y0 + y1) / 2 - tamanio * 0.5],
        texto, fill=(0, 0, 0), font=ImageFont.truetype(TTF, tamanio))


def crear_palo(draw, xy, n, lista_cq, l_i):
    x, y = xy
    font = ImageFont.truetype(TTF,size=40)
    draw.text([xy[0] - 75, xy[1] + 5], "x" + str(n), fill=(0, 0, 0),font=font)
    xi = 0
    for corte, cantidad in lista_cq:
        if cantidad != 0:
            for _ in range(cantidad):
                coords = [x + xi, y, x + xi + corte * 2, y + 50]
                crea_rectangulo(draw, coords, ANCHO)
                if corte % 1 == 0:
                    corte = int(corte)
                centrar_texto(draw, coords, str(corte))
                xi += corte * 2
        coords = [x + xi, y, x + l_i * 2, y + 50]
        crea_rectangulo(draw, coords, ANCHO, (100, 100, 100))


def crear_palos(draw, xy, n_lista_cq, l_i):
    x, y = xy
    for n, lista_cq in n_lista_cq:
        crear_palo(draw, [x, y], n, lista_cq, l_i)
        y += 70


def crear_imagen_palo(constru, material, n_lista_cq, l_i):
    i = 0
    n = 7
    while n_lista_cq:
        im = Image.new("RGB", (800, 600), (255, 255, 255))
        draw = ImageDraw.Draw(im)
        font = ImageFont.truetype(TTF,size=40)
        draw.text([50, 15], material, fill=(0, 0, 0), font=font)
        crear_palos(draw, (100, 100), n_lista_cq[:n], l_i)
        direccion = "./imagenes/"
        if not os.path.exists(direccion):
            os.makedirs(direccion)
        nombre = constru + " " + material
        if i:
            nombre += " _" + str(i)
        im.save(direccion + nombre + ".jpg", "JPEG")
        n_lista_cq = n_lista_cq[n:]
        i += 1
