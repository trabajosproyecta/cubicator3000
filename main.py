from subprocess import call
from drawer import *
from excel_handler import *
import numpy as np

def g2_patterns(cq, maxl):
    patts = []
    if not cq:
        return patts
    npatt = [0 for _ in cq]
    corte, _ = cq[0]
    while maxl >= 0:
        returns = g2_patterns(cq[1:], maxl)
        for ret in returns:
            patts.append(npatt[:1] + ret)
        patts.append(list(npatt))
        maxl -= corte
        npatt[0] += 1
    return patts


'''
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
'''


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
    cuts = [a for a, b in cortes_cantidad]
    qs = [b for a, b in cortes_cantidad]
    cq = [[a, b] for a, b in zip(cuts, qs)]

    patterns = g2_patterns(cq, largos[material])

    # writedata(NDATA, patterns, cq, cuts)
    #
    # writemodel(NMODEL, modelstring)
    #
    # writerun(NRUN, runstring)
    #
    # with open(os.devnull, "w") as f:
    #     call("ampl "+NRUN, stdout=f)
    #
    # optimum = get_results(NAMPLOUT, patterns)

    ## ACA LLAMAR A MODELO DE PULP

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
            nums = nums[:largo - i] + "." + nums[largo - i:]
    return nums


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


'''
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
'''

if __name__ == "__main__":
    comenzar()
