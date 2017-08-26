import pulp
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

def cleared_patterns(cq,maxl):
    cleared = np.unique([tuple(x) for x in g2_patterns(cq, maxl)],axis=0)
    return cleared

def create_model(cuts_quantity,patterns):
    pass

def get_results(model):
    pass