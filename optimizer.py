import os
from functools import reduce
from subprocess import call
import xlrd
import xlwt
from PIL import Image, ImageDraw, ImageFont


def suma_vectores(v, v2):
    return [a+b for a, b in zip(v, v2)]


def copylist(lista):
    return [a for a in lista]


def g2_patterns(cq, maxl):
    patts = []
    if not cq:
        return patts
    npatt = [0 for tupla in cq]
    corte, _ = cq[0]
    while maxl >= 0:
        returns = g2_patterns(cq[1:], maxl)
        for ret in returns:
            patts.append(npatt[:1] + ret)
        patts.append(copylist(npatt))
        maxl -= corte
        npatt[0] += 1
    return patts


def writemodel(nombre, mstring):
    with open(nombre, "w") as archivomodelo:
        archivomodelo.write(mstring)


def writerun(nombre, rstring):
    with open(nombre, "w") as archivorun:
        archivorun.write(rstring)


def writedata(nombre, patterns, cq, cuts):
    with open(nombre, "w") as archivodat:
        archivodat.write("data; \n\n")
        archivodat.write("set CUTS := "+str(cuts[0]))
        for cut in cuts[1:]:
            archivodat.write(", "+str(cut))
        archivodat.write(";\n\n")
        archivodat.write("set PATTERNS := 1")
        for i, _ in enumerate(patterns[1:]):
            archivodat.write(", " + str(i+2))
        archivodat.write(";\n\n")
        archivodat.write("param cantidad :=")
        for corte, num in cq:
            archivodat.write("\n\t" + str(corte) + "\t\t" + str(num))
        archivodat.write(";\n\n")
        archivodat.write("param q :")
        for i, _ in enumerate(patterns):
            archivodat.write("\t"+str(i+1))
        archivodat.write(":=")
        for i, corte in enumerate(cuts):
            archivodat.write("\n")
            archivodat.write("\t"+str(corte)+"\t")
            for pattern in patterns:
                archivodat.write("\t" + str(pattern[i]))
        archivodat.write(";\n")


def get_results(nombre, patterns):
    ret = []
    with open(nombre, "r") as archivores:
        lineas = archivores.readlines()
        nlineas = len(lineas)
        for linea in lineas[1:nlineas-4]:
            llinea = linea.strip().split(" ")
            npatron, cantidad = [a for a in llinea if a]
            cantidad = int(cantidad)
            patron = patterns[int(npatron)-1]
            ret.append([cantidad, patron])
    return ret


def string_results(nombre, optimum, cuts, precio):
    totalcortes = [0 for cut in cuts]
    s = "\t" + "-"*50 + "\n"
    s += "\t -- " + nombre + " --\n\n\t\t"
    for corte in cuts:
        s += str(corte).ljust(6) + "\t"
    s += "\n"
    for cantidad, patron in optimum:
        s += "\t" + str(cantidad) + "\t"
        for i, ncortes in enumerate(patron):
            totalcortes[i] += ncortes*cantidad
            if ncortes == 0:
                ncortes = "-"
            s += str(ncortes).ljust(6) + "\t"
        s += "\t"+str(sum([a*b for a, b in zip(patron, cuts)]))+"\n"
    npalos = sum([a for a, b in optimum])
    s += "\t\t"
    for corte in totalcortes:
        s += str(corte).ljust(6) + "\t"
    s += "\n\n\tTotal: " + str(npalos)
    s += "\t\tPrecio: $" + tointstr(npalos*precio)
    return s


def delfiles(names):
    for name in names:
        s = "del .\\" + name
        call(s, shell=True)


def get_excel(nombre):
    book = xlrd.open_workbook(nombre)
    sn = book.sheet_names()

    construcciones = sn[1:]
    lmateriales = []
    metadata = book.sheet_by_name(sn[0])

    L_material = {}             # Diccionario {Tabla: Largo inicial}
    precio_material = {}        # Diccionario {Tabla: precio}
    for i in range(1, metadata.nrows):
        lmateriales.append(metadata.cell(i, 0).value)
        L_material[metadata.cell(i, 0).value] = metadata.cell(i, 1).value
        precio_material[metadata.cell(i, 0).value] = metadata.cell(i, 2).value

    ret = {}

    for constru in construcciones:
        sheet = book.sheet_by_name(constru)
        if sheet.nrows <= 1:  # Si no hay filas en la hoja...
            print("Nada que optimizar en " + constru + "...")
            continue

        materiales = {}
        for i in range(1, sheet.nrows):
            material_actual = sheet.cell(i, 1).value   # String unicode
            corte_actual = sheet.cell(i, 2).value      # float
            ncortes_actual = sheet.cell(i, 3).value    # float
            if material_actual not in materiales:
                materiales[material_actual] = {}
            if corte_actual not in materiales[material_actual]:
                materiales[material_actual][corte_actual] = 0
            materiales[material_actual][corte_actual] += ncortes_actual

        ret[constru] = materiales

    retorno = {}

    for constru in ret:
        retorno[constru] = {}
        for mater in ret[constru]:
            retorno[constru][mater] = []
            for corte in ret[constru][mater]:
                retorno[constru][mater].append([corte,
                    int(ret[constru][mater][corte])])

    return L_material, precio_material, retorno, (construcciones, lmateriales)


def optimize(cortes_cantidad, construccion, material, largos,
        patrones_optimos, precios):
    """
    cortes_cantidad: [[float(largo del corte), int(cantidad)], ]
    construccion: str(construccion)
    material: str(material)

    retorna string con los cortes y el numero de palos que se usaron
    """

    nombre = " -- " + construccion + " - " + material + " -- "
    cuts = [a for a, b in cortes_cantidad]
    qs = [b for a, b in cortes_cantidad]
    cq = [[a, b] for a, b in zip(cuts, qs)]

    patterns = g2_patterns(cq, largos[material])

    writedata(NDATA, patterns, cq, cuts)

    writemodel(NMODEL, modelstring)

    writerun(NRUN, runstring)

    with open(os.devnull, "w") as f:
        call("ampl "+NRUN, stdout=f)

    optimum = get_results(NAMPLOUT, patterns)

    # [(np, [(corte, nc), ]), ]
    aa = list(zip([n for n, _ in optimum],
                  [list(zip(cuts, p)) for _, p in optimum]))

    # Agregando al diccionario de optimos
    if construccion not in patrones_optimos:
        patrones_optimos[construccion] = {}

    patrones_optimos[construccion][material] = aa

    sresults = string_results(nombre, optimum, cuts, precios[material])

    delfiles([NDATA, NMODEL, NRUN, NAMPLOUT])

    return sresults, sum([a for a, b in optimum])


def tointstr(numero):
    nums = str(int(numero))
    largo = len(nums)
    for i, _ in enumerate(nums):
        if i % 3 == 0 and i != 0:
            nums = nums[:largo-i] + "." + nums[largo-i:]
    return nums


# Funciones para imagenes:


def crea_rectangulo(draw, xyxy, ancho, fill=(255, 255, 255)):
    for i in range(ancho):
        draw.rectangle([x-i for x in xyxy], outline=(0, 0, 0), fill=fill)


def centrar_texto(draw, xyxy, texto):
    x0, y0, x1, y1 = xyxy
    tamanio = int(min(max((x1 - x0)/8 + 10, 5), 40))
    draw.text(
        [max(x0, (x0 + x1)/2 - len(texto)*tamanio*0.35),
         (y0 + y1)/2 - tamanio*0.5],
        texto, fill=(0, 0, 0), font=ImageFont.truetype(TTF, tamanio))


def crear_palo(draw, xy, n, lista_cq, l_i):
    x, y = xy
    font = ImageFont.truetype(TTF, 40)
    draw.text([xy[0]-75, xy[1] + 5], "x"+str(n), fill=(0, 0, 0), font=font)
    xi = 0
    for corte, cantidad in lista_cq:
        if cantidad != 0:
            for _ in range(cantidad):
                coords = [x + xi, y, x + xi + corte*2, y + 50]
                crea_rectangulo(draw, coords, ANCHO)
                if corte % 1 == 0:
                    corte = int(corte)
                centrar_texto(draw, coords, str(corte))
                xi += corte*2
        coords = [x + xi, y, x + l_i*2, y+50]
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
        font = ImageFont.truetype(TTF, 40)
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


def cubicar_por_proyecto(patrones_optimos):
    dic_proyectos = {}
    for constru in patrones_optimos:
        if constru not in dic_proyectos:
            dic_proyectos[constru] = {}
        for material in patrones_optimos[constru]:
            dic_proyectos[constru][material] = sum(
                [n for n, _ in patrones_optimos[constru][material]])
    return dic_proyectos


def crear_excel(cubicacion_por_proyecto, nombre, lo_con, lo_mat):
    materiales_usados = set(reduce(lambda a, b: a+b,
        [list(mats.keys()) for mats in cubicacion_por_proyecto.values()]))
    lo_con = [con for con in lo_con if con in cubicacion_por_proyecto]
    lo_mat = [mat for mat in lo_mat if mat in materiales_usados]

    wb = xlwt.Workbook()
    ws = wb.add_sheet("Cubicaciones")

    borderstring = "borders: right thin, left thin, top thin, bottom thin"
    colorstring = "pattern: pattern solid, fore_colour light_green"

    boldstyle = xlwt.easyxf("font:bold on; " + borderstring)
    bordstyle = xlwt.easyxf(borderstring)
    normstyle = xlwt.easyxf(borderstring + "; " + colorstring)

    for i in range(len(lo_con) + 1):
        ws.col(i).width = 4000

    for nproyecto in cubicacion_por_proyecto:
        proyecto = cubicacion_por_proyecto[nproyecto]
        index_con = lo_con.index(nproyecto) + 1
        ws.write(0, index_con, nproyecto, boldstyle)
        for nmaterial in proyecto:
            cmaterial = proyecto[nmaterial]
            try:
                ws.write(lo_mat.index(nmaterial) + 1, 0, nmaterial, boldstyle)
            except Exception as err:
                if "Attempt to overwrite" not in str(err):
                    raise Exception(err)
            ws.write(lo_mat.index(nmaterial) + 1, index_con, cmaterial,
                     normstyle)

    for i in range(len(lo_mat) + 1):
        for j in range(len(lo_con)+1):
            try:
                ws.write(i, j, "", bordstyle)
            except Exception as err:
                if "Attempt to overwrite" not in str(err):
                    raise Exception(err)

    wb.save(nombre)


def comenzar():
    largos, precios, diccionario, listas_ordenadas = get_excel(NOMBREEXCEL)
    lo_construcciones, lo_materiales = listas_ordenadas

    patrones_optimos = {}

    sfinal = ""
    for construccion in diccionario:
        print("Optimizando " + construccion + "...")
        total = 0
        totalpalos = {}
        for material in diccionario[construccion]:
            sresults, n = optimize(diccionario[construccion][material],
                construccion, material, largos, patrones_optimos, precios)
            sfinal += sresults + "\n\n"
            total += n*precios[material]
            totalpalos[material] = n
        sfinal += "\n" + "*"*60
        sfinal += "\nTOTAL " + construccion + ": \n"
        for material in totalpalos:
            sfinal += material + ": " + str(int(totalpalos[material])) + "\n"
        sfinal += " ---- Total: $" + tointstr(total) + " ---- \n"
        sfinal += "*"*60 + "\n\n\n"

    i = 1
    nresult = NRESULT
    while nresult in os.listdir():
        nresult = NRESULT[:-4] + " (" + str(i) + ")" + NRESULT[-4:]
        i += 1

    with open(nresult, "w") as archivo:
        archivo.write(sfinal)

    print("Listo!! Resultados de la optimizacion guardados en " + nresult)
    print("Guardando imagenes...")

    for constru in patrones_optimos:
        for material in patrones_optimos[constru]:
            crear_imagen_palo(constru, material,
                patrones_optimos[constru][material], largos[material])

    print("Imagenes guardadas! Creando excel...")

    cubicacion_por_proyecto = cubicar_por_proyecto(patrones_optimos)
    nexcelresult = nresult[:-4] + ".xls"
    crear_excel(cubicacion_por_proyecto, nexcelresult,
        lo_construcciones, lo_materiales)

    print("Listo! Excel guardado en " + nexcelresult)


TTF = "arial.ttf"
ANCHO = 2

NDATA = "optdata.dat"
NMODEL = "optmodel.mod"
NRUN = "optrun.run"
NAMPLOUT = "optxz.txt"
NRESULT = "optresult.txt"
NOMBREEXCEL = "cubicacion.xlsx"

modelstring = (
    """
#Parametros

set CUTS;
set PATTERNS;

param cantidad {CUTS};

param q {CUTS, PATTERNS};

# VARIABLE
var x {PATTERNS} integer >= 0;

# FO
minimize z: sum {j in PATTERNS} x[j];

# RESTRICCIONES

subject to restriccion1 {i in CUTS}:
        cantidad[i] == sum {j in PATTERNS} (x[j])*(q[i, j]);
"""
)

runstring = (
    """
option solver cplex;
model {} ;
data {};
solve ;
option omit_zero_rows 1;
display x, z >{};
""".format(NMODEL, NDATA, NAMPLOUT)
)


if __name__ == "__main__":

    comenzar()