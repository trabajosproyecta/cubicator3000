from pulp import LpProblem, LpMinimize, LpVariable, LpInteger, lpSum, pulp
import numpy as np
import os


def get_patterns(cq, maxl):
    patts = []
    if not cq:
        return patts
    npatt = [0 for _ in cq]
    corte, _ = cq[0]
    while maxl >= 0:
        returns = get_patterns(cq[1:], maxl)
        for ret in returns:
            patts.append(npatt[:1] + ret)
        patts.append(list(npatt))
        maxl -= corte
        npatt[0] += 1
    return patts


def cleared_patterns(cq, maxl):
    cleared = np.unique([tuple(x) for x in get_patterns(cq, maxl)], axis=0)
    return cleared


def create_model(cuts_quantity, maxl):
    patterns = get_patterns(cuts_quantity, maxl)
    model = LpProblem("Cubicator3000", LpMinimize)

    '''
    patterns is a array of vectors. i=1...n, j=1..m
    cuts is a array of floats j=1..m
    X_i is int variable for times the pattern is used.
    '''

    dict_X = {}
    n = len(patterns)
    m = len(cuts_quantity)

    for i in range(n):
        dict_X[i] = LpVariable("Pattern {} gets used".format(i), cat=LpInteger,
                               lowBound=0)
        dict_X[i].index = i

    # F.O sum over X variables
    model += lpSum([dict_X[i] for i in range(n)]), "Minimize tables used"
    # restrictions: the amount of every cut should be the amount demanded
    for j in range(m):
        temp_var = lpSum([dict_X[i] * patterns[i][j] for i in range(n)])
        temp_string = "the amount of cut {} produced equals the demanded"
        model += temp_var == cuts_quantity[j][1], temp_string.format(j)
    return model, patterns


def solve(model, patterns):
    cwd = os.getcwd()
    # extracted and renamed CBC solver binary
    # solverdir = 'cbc-2.7.5-win64\\bin\\cbc.exe'  # windows
    # solverdir = 'Cbc-2.4.0-linux-x86_64/bin/cbc'  # linux
    # solverdir = 'cbc/linux/64/cbc'  # Linux
    # solverdir = os.path.join(cwd, solverdir)
    # solver = pulp.COIN_CMD(path=solverdir)
    # model.solve(solver)
    model.solve()
    # print("Solving")
    # print(LpStatus[model.status])
    # model.solve()
    results = {}
    for x in model.variables():
        if x.varValue > 0:
            results[tuple(patterns[x.index])] = x.varValue
    return results
