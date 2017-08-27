from subprocess import call
from cubicator.drawer import *
from cubicator.excel_handler import *
from cubicator.optimizer import *
from copy import deepcopy


def get_results(nombre, patterns):
    ret = []
    with open(nombre, "r") as archivores:
        lineas = archivores.readlines()
        nlineas = len(lineas)
        for linea in lineas[1:nlineas - 4]:
            llinea = linea.strip().split(" ")
            npatron, cantidad = [a for a in llinea if a]
            cantidad = int(cantidad)
            patron = patterns[int(npatron) - 1]
            ret.append([cantidad, patron])
    return ret


def string_results(nombre, optimum, cuts, precio):
    totalcortes = [0 for _ in cuts]
    s = "\t" + "-" * 50 + "\n"
    s += "\t -- " + nombre + " --\n\n\t\t"
    for corte in cuts:
        s += str(corte).ljust(6) + "\t"
    s += "\n"
    for cantidad, patron in optimum:
        s += "\t" + str(cantidad) + "\t"
        for i, ncortes in enumerate(patron):
            totalcortes[i] += ncortes * cantidad
            if ncortes == 0:
                ncortes = "-"
            s += str(ncortes).ljust(6) + "\t"
        s += "\t" + str(sum([a * b for a, b in zip(patron, cuts)])) + "\n"
    npalos = sum([a for a, b in optimum])
    s += "\t\t"
    for corte in totalcortes:
        s += str(corte).ljust(6) + "\t"
    s += "\n\n\tTotal: " + str(npalos)
    s += "\t\tPrecio: $" + tointstr(npalos * precio)
    return s


def delfiles(names):
    for name in names:
        s = "del .\\" + name
        call(s, shell=True)


def optimize(cortes_cantidad, construccion, material, largos,
             patrones_optimos, precios):
    """
    cortes_cantidad: [[float(largo del corte), int(cantidad)], ]
    construccion: str(construccion)
    material: str(material)

    retorna string con los cortes y el numero de palos que se usaron
    """

    nombre = " -- " + construccion + " - " + material + " -- "
    print(nombre)
    print(cortes_cantidad)
    #copy of cortes_cantidad
    cq = deepcopy(cortes_cantidad)
    cuts = list(map(lambda x: x[0],cortes_cantidad))
    model, patterns = create_model(cq, largos[material])
    result = solve(model, patterns)
    print(result)


    #transformación de resultado para retrocompatibilidad
    optimum = [[result[x],x] for x in result]

    aa = list(zip([result[p] for p in result],[list(zip(cuts, p)) for p in result]))

    # Agregando al diccionario de optimos. El verdadero output de la optimización es al hacer esto.
    if construccion not in patrones_optimos:
        patrones_optimos[construccion] = {}

    patrones_optimos[construccion][material] = aa
    sresults = string_results(nombre, optimum, cuts, precios[material])

    return sresults, sum([a for a, b in optimum])


def tointstr(numero):
    nums = str(int(numero))
    largo = len(nums)
    for i, _ in enumerate(nums):
        if i % 3 == 0 and i != 0:
            nums = nums[:largo - i] + "." + nums[largo - i:]
    return nums


def start():
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
            total += n * precios[material]
            totalpalos[material] = n
        sfinal += "\n" + "*" * 60
        sfinal += "\nTOTAL " + construccion + ": \n"
        for material in totalpalos:
            sfinal += material + ": " + str(int(totalpalos[material])) + "\n"
        sfinal += " ---- Total: $" + tointstr(total) + " ---- \n"
        sfinal += "*" * 60 + "\n\n\n"

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


def cubicar_por_proyecto(patrones_optimos):
    dic_proyectos = {}
    for constru in patrones_optimos:
        if constru not in dic_proyectos:
            dic_proyectos[constru] = {}
        for material in patrones_optimos[constru]:
            dic_proyectos[constru][material] = sum(
                [n for n, _ in patrones_optimos[constru][material]])
    return dic_proyectos

NOMBREEXCEL = "../cubicacion.xlsx"
NRESULT = "../optresult.txt"

if __name__ == "__main__":
    start()
