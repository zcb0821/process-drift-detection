HOLD = 1
HALF_HOLD = 2
NOT_HOLD = 0

# def ExRORU_direct_causal(trace):
#    pass
# def ExRORU_indirect_causal(trace):
#     follow_sets = {}
#     for i in xrange(len(trace)):
#         fs = set()
#         for j in xrange(i + 1, len(trace)):
#             fs.add(trace[j])
#             if trace[i] == trace[j]:
#                 break
#         union, intersection = follow_sets.setdefault(trace[i], (set(), set()))
#         follow_sets[trace[i]] = (union.union(fs), intersection.intersection(fs))
    
#     relations = 
#     for transition,


# def ExRORU_direct_reverse_causal(trace):
#     pass

# def ExRORU_indiret_reverse_causal(trace):
#     pass


def direct_causal(trace):
    relations = {}
    for i in xrange(len(trace)-1):
        name = '%s,%s' % (trace[i], trace[i + 1])
        relations[name] = ((trace[i], trace[i + 1]), HOLD)
    return relations.values()
        


def indirect_causal(trace):
    relations = {}
    for i in xrange(len(trace)-1):
        for j in xrange(i+1, len(trace)):
            name = '%s,%s' % (trace[i], trace[j])
            relations[name] = ((trace[i], trace[i + 1]), HOLD)
    return relations.values()
    

def co_exist(trace):
    relations = {}
    for i in xrange(len(trace)):
        for j in xrange(i + 1, len(trace)):
            if trace[i] <= trace[j]:
                name = '%s,%s' % (trace[i], trace[j])
                relations[name] = ((trace[i], trace[j]), HOLD)
            else:
                name = '%s,%s' % (trace[j], trace[i])
                relations[name] = ((trace[j], trace[i]), HOLD)
    return relations.values()


