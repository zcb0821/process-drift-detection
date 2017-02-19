# encoding: utf-8
import birelations
import merge
import partition

from log import *


def print_table(table, header):
    for i in xrange(len(table)):
        print header[i],
        for j in xrange(len(table[i])):
            print table[i][j],
        print


class DriftDetector:
    def __init__(self):
        self.min_len = 100
        self.noise_tolerance = 0
        self.r_types = [(birelations.direct_causal, 'all')]

        self.r_matrix = None
        self.traces = None
        self.partitions = None

        self.console_output = False

    def detect(self, source):
        if isinstance(source, str):
            # source of string type represents a file path.
            # The detector will read log from mxml file.
            # print 'parsing log file %s ...' % source
            log = mxml.parse(source)
            self.traces = log['traces']
            # print 'parsing log file successfully' % source
        elif isinstance(source, list):
            self.traces = source
        else:
            raise '参数 source 必须为数组或字符串'

        # generate detection table
        print 'generate detection table...'
        self.r_matrix = {
            'relations': [],
            'data': [],
            'partitions': []
        }
        generator = birelations.BIRTableGenerator(self.traces)
        for r_type in self.r_types:
            func, level = r_type
            data, relations = generator.generate(func, level)
            self.r_matrix['relations'].extend(relations)
            self.r_matrix['data'].extend(data)
        if self.console_output:
            print_table(self.r_matrix['data'], self.r_matrix['relations'])

        # print 'generate detection table successfully'

        # partition each relation item
        print 'partitioning'
        num_of_relation = len(self.r_matrix['relations'])
        all_intervals = set()
        for i in xrange(num_of_relation):
            intervals = partition.partition_2(self.r_matrix['data'][i],
                                              min_len=self.min_len)
            self.r_matrix['partitions'].append(intervals)
            all_intervals = all_intervals.union(intervals)
            if self.console_output:
                print intervals

        # merge partitions
        print 'merging'
        result = merge.merge_by_dbscan(all_intervals, (0, len(self.traces)), self.min_len, self.min_len * 0.05, 2)
        return result


def save_table(table, filepath):
    with open(filepath, 'w') as f:
        (a, b, c) = table.shape
        for i in xrange(a):
            for j in xrange(b):
                f.writelines([str(v) for v in table[i][j]])
                f.write('\n')


if __name__ == '__main__':
    pass
