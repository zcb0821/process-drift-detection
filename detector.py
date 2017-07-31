# encoding: utf-8
import birelations
import merge
import partition

from log import *
import heapq


def print_table(table, header):
    for i in xrange(len(table)):
        print header[i],
        for j in xrange(len(table[i])):
            print table[i][j],
        print


class DriftDetector:
    def __init__(self, min_len=100, radius=10):
        self.min_len = min_len
        self.radius = radius
        self.min_pts = 1

        self.noise_tolerance = 0
        self.r_types = [(birelations.direct_causal, 'all')]

        self.r_matrix = None
        self.traces = None
        self.partitions = None

        self.console_output = False

    def set_log(self, source):
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
            raise '参数 source 必须为字符串数组或文件路径字符串'

    def extract(self):
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

    def partition(self, min_len):
        self.r_matrix['partitions'] = []
        for row in self.r_matrix['data']:
            intervals = partition.partition_2(row, min_len)
            self.r_matrix['partitions'].append(intervals)

    def combine(self):
        all_intervals = set()
        for intervals in enumerate(self.r_matrix['partitions']):
            all_intervals.union(intervals)
        result = merge.merge_by_dbscan(all_intervals, (0, len(
            self.traces)), self.min_len, self.radius, self.min_pts)
        return result

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
        if self.console_output:
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
        if self.console_output:
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
        if self.console_output:
            print 'merging'
        result = merge.merge_by_dbscan(all_intervals, (0, len(
            self.traces)), self.min_len, self.radius, self.min_pts)
        return result

    def candidates(self):
        N = len(self.traces)
        X = []
        Y = []
        for i, intervals in enumerate(self.r_matrix['partitions']):
            for interval in intervals:
                if interval[0] != 0 and interval[0] != N:
                    X.append(interval[0])
                    Y.append(i)
                if interval[1] != 0 and interval[1] != N:
                    X.append(interval[1])
                    Y.append(i)
        return X, Y


class OnlineDetector:
    def __init__(self, min_len):
        self.min_len = min_len
        self.r_funcs = {
            'dc': birelations.direct_causal,
        }
        self.sensors = {}
        self.counter = 0
        self.window = []
        self.window_size = int(self.min_len * 0.05)
        self.sensibility = 1
        self.last_change = 0

    def receive(self, trace):
        map = {}
        for r_func_name, r_func in self.r_funcs.iteritems():
            for r in r_func(trace):
                r_name = "%s-%s-%s" % (r_func_name, r[0][0], r[0][1])
                r_value = r[1]
                map[r_name] = r_value
                self.sensors.setdefault(r_name, Sensor(self.min_len))
        for name, sensor in self.sensors.iteritems():
            if name in map:
                change = sensor.receive(map[name], self.counter)
            else:
                change = sensor.receive(0, self.counter)
            if change is not None:
                while self.window and abs(change - self.window[0] + 1) > self.window_size:
                    heapq.heappop(self.window)
                heapq.heappush(self.window, change)

        self.counter += 1
        if len(self.window) >= self.sensibility:
            avg = sum(self.window) / len(self.window)
            self.window = []
            if avg - self.last_change >= self.min_len:
                self.last_change = avg
                return avg
        else:
            return None

    def detect(self, traces):
        result = [0]
        delay = [0]
        for i, trace in enumerate(traces):
            change = self.receive(trace)
            if change is not None:
                result.append(change)
                delay.append(i)
        result.append(len(traces))
        delay.append(len(traces))
        return result, delay


class Sensor:
    def __init__(self, min_len):
        self.min_len = min_len
        self.observing = None
        self.begin = 0
        self.count = 0
        self.last_change = 0

    def receive(self, value, index):
        change = None
        if self.observing != value:
            if self.count >= self.min_len or (self.observing is None and index >= self.min_len):
                change = index
                self.last_change = change
            self.observing = value
            self.count = 1
            self.begin = index
        else:
            self.count += 1
            if self.begin != self.last_change and self.count >= self.min_len:
                change = self.begin
                self.last_change = change
        return change


def save_table(table, filepath):
    with open(filepath, 'w') as f:
        (a, b, c) = table.shape
        for i in xrange(a):
            for j in xrange(b):
                f.writelines([str(v) for v in table[i][j]])
                f.write('\n')


if __name__ == '__main__':
    pass
