# encoding: utf-8
import numpy as np
HOLD = 1
NOT_HOLD = 0
NULL = -1


def direct_causal(trace):
    relations = {}
    for i in xrange(len(trace)-1):
        name = '%s,%s' % (trace[i], trace[i + 1])
        relations[name] = ((trace[i], trace[i + 1]), HOLD)
    return relations.values()


def weak_causal(trace):
    relations = {}
    for i in xrange(len(trace)-1):
        for j in xrange(i+1, len(trace)):
            name = '%s,%s' % (trace[i], trace[j])
            relations[name] = ((trace[i], trace[j]), HOLD)
    return relations.values()
    

def co_exist(trace):
    relations = {}
    for i in xrange(len(trace)):
        for j in xrange(i + 1, len(trace)):
            if trace[i] <= trace[j]:
                first, second = trace[i], trace[j]
            else:
                first, second = trace[j], trace[i]
            name = '%s,%s' % (first, second)
            relations[name] = ((first, second), HOLD)
    return relations.values()


class BIRTableGenerator:
    def __init__(self, traces):
        self.traces = traces
        self.t_flags = {}
        self.calculate_transition_flags()

    def generate(self, relation_func, level):
        r_to_idx = {}
        r_data = []
        r_list = []
        for index, trace in enumerate(self.traces):
            rs = relation_func(trace)
            for r_tuple, r_value in rs:
                key = '%s, %s' % (r_tuple[0], r_tuple[1])
                idx = r_to_idx.get(key)
                if idx is None:
                    idx = len(r_data)
                    r_to_idx[key] = idx
                    r_list.append(r_tuple)
                    r_data.append(self.new_data_item(r_tuple, level))
                r_data[idx][index] = r_value
        return r_data, r_list

    def new_data_item(self, r_tuple, level):
        if level == 'all':
            return np.full(len(self.traces), NOT_HOLD, np.int8)
        elif level == 'first':
            return np.copy(self.t_flags[r_tuple[0]])
        elif level == 'second':
            return np.copy(self.t_flags[r_tuple[1]])
        else:
            raise Exception()

    def calculate_transition_flags(self):
        """
        返回每个变迁在每条 trace 上的存在情况
        存在记为 0, 对应二元关系不成立
        不存在记为 -1，对应二元关系不存在
        """
        self.t_flags = {}
        for index, trace in enumerate(self.traces):
            for transition in trace:
                flags = self.t_flags.setdefault(transition, np.full(len(self.traces), NULL, np.int8))
                flags[index] = NOT_HOLD
