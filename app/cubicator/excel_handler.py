import xlrd
import xlwt
from functools import reduce


def get_excel(nombre):
    book = xlrd.open_workbook(nombre)
    sheet_names = book.sheet_names()  # ['Precios', 'Juego dos Torres', ...]
    constructions = sheet_names[1:]
    metadata = book.sheet_by_name(sheet_names[0])

    boards_list = []  # ['Cuarton', '2x4 Bruto', ...]
    board_initial_length = {}  # {'Cuarton': 320.0, '2x4 Bruto': 320.0, ...}
    board_price = {}  # {'Cuarton': 4200.0, '2x4 Bruto': 3200.0, ...}

    for i in range(1, metadata.nrows):  # for each row:
        # Retrive values
        name = metadata.cell(i, 0).value
        initial_length = metadata.cell(i, 1).value
        price = metadata.cell(i, 2).value

        # Add to objects
        boards_list.append(name)
        board_initial_length[name] = initial_length
        board_price[name] = price

    all_cuts = {}

    for construction in constructions:
        sheet = book.sheet_by_name(construction)
        if sheet.nrows <= 1:  # Si no hay filas en la hoja...
            continue

        boards_cuts = {}
        for i in range(1, sheet.nrows):  # For each row in this construction
            current_board = sheet.cell(i, 1).value  # String unicode
            current_cut = sheet.cell(i, 2).value  # float
            current_cut_quantity = sheet.cell(i, 3).value  # float

            # Add this cut quantity to total cut quantites
            if current_board not in boards_cuts:
                boards_cuts[current_board] = {}
            if current_cut not in boards_cuts[current_board]:
                boards_cuts[current_board][current_cut] = 0
            boards_cuts[current_board][current_cut] += current_cut_quantity

        all_cuts[construction] = boards_cuts

    for construction in all_cuts:
        for board in all_cuts[construction]:
            aux = []
            for cut in all_cuts[construction][board]:
                aux.append([cut, int(all_cuts[construction][board][cut])])
            all_cuts[construction][board] = aux

    return board_initial_length, board_price, all_cuts, \
        (constructions, boards_list)


def crear_excel(cubicacion_por_proyecto, nombre, lo_con, lo_mat):
    materiales_usados = set(
        reduce(lambda a, b: a + b, [list(mats.keys()) for mats in
                                    cubicacion_por_proyecto.values()]))
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
