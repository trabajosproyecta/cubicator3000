import xlrd
import xlwt
from functools import reduce


def get_excel(nombre):
    book = xlrd.open_workbook(nombre)
    sn = book.sheet_names()

    construcciones = sn[1:]
    lmateriales = []
    metadata = book.sheet_by_name(sn[0])

    L_material = {}  # Diccionario {Tabla: Largo inicial}
    precio_material = {}  # Diccionario {Tabla: precio}
    for i in range(1, metadata.nrows):
        lmateriales.append(metadata.cell(i, 0).value)
        L_material[metadata.cell(i, 0).value] = metadata.cell(i, 1).value
        precio_material[metadata.cell(i, 0).value] = metadata.cell(i, 2).value

    ret = {}

    for constru in construcciones:
        sheet = book.sheet_by_name(constru)
        if sheet.nrows <= 1:  # Si no hay filas en la hoja...
            #print("Nada que optimizar en " + constru + "...")
            continue

        materiales = {}
        for i in range(1, sheet.nrows):
            material_actual = sheet.cell(i, 1).value  # String unicode
            corte_actual = sheet.cell(i, 2).value  # float
            ncortes_actual = sheet.cell(i, 3).value  # float
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


def crear_excel(cubicacion_por_proyecto, nombre, lo_con, lo_mat):
    materiales_usados = set(reduce(lambda a, b: a + b,
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
        for j in range(len(lo_con) + 1):
            try:
                ws.write(i, j, "", bordstyle)
            except Exception as err:
                if "Attempt to overwrite" not in str(err):
                    raise Exception(err)

    wb.save(nombre)
