# encoding: utf-8
import mxml
import numpy as np
import birelations


def generate(traces, relation_func, frequency_level='all'):
    relation_dict = {}
    for index, trace in enumerate(traces):
        if frequency_level != 'all':
            for value in relation_dict.itervalues():
                transition = value['relation'][0] if frequency_level == 'first' else value['relation'][1]
                if transition not in trace:
                    value['data'][index] = -1
        rs = relation_func(trace)
        for r in rs:
            data = relation_dict.setdefault(str(r[0]), np.zeros(len(traces), np.uint8))
            data[index] = r[1]
        
    data = np.array([v['data'] for v in relation_dict.itervalues()])
    return data     
        

class DriftDetector():
    def __init__(self):
        self.window_size = 100
        self.noise_tolerance = 1
        self.relations = [birelations.direct_causal, birelations.indirect_causal, birelations.co_exist]
        self.frequency_levels = ['first']
        self.enable_partition_compatible = True

        self.table = None
        self.traces = None
        self.partitions = None

    def detect(self, filepath):
        # read log from mxml file
        print 'parsing log file %s ...' % filepath
        log = mxml.parse(filepath)
        self.traces = log['traces']
        print 'parsing log file successfully' % filepath

        # generate detection table
        print 'generate detection table...'
        self.table = None
        for r in self.relations:
            for f in self.frequency_levels:
                if self.table is None:
                    self.table = generate(self.traces, r, f)
                else:
                    self.table = np.vstack((self.table, generate(self.traces, r, f)))
        print 'generate detection table successfully'

        # partition each relation stream
        print 'partitioning'
        number_of_rows, number_of_cols = self.table.shape
        self.partitions = []
        for i in xrange(number_of_rows):
            partitions = self.partition(self.table.data[i])
            self.partitions.append(partitions)

        # merge partitions
        result = self.merge()
        print result

    def merge(self):
        left_points = []
        right_points = []

        for partitions in self.partitions:
            for range in partitions:
                left_points.append(range[0])
                right_points.append(range[1])

        if self.enable_partition_compatible:
            left_clusters = self.cluster(left_points)
            right_clusters = self.cluster(right_points)

            refined_left_points = [cluster[0] for cluster in left_clusters]
            refined_right_points = [cluster[-1] for cluster in right_clusters]

            clusters = self.cluster(refined_left_points + refined_right_points)
        else:
            clusters = self.cluster(left_points + right_points)

        result = [0]
        for cluster in clusters:
            center = int(sum(cluster) / len(cluster))
            if center - result[-1] >= self.window_size:
                result.append(center)
        return result
        
    def cluster(self, points, eps=5):
        points.sort()
        
        clusters = []
        cluster = []

        for p in points:
            if not cluster or abs(p - cluster[-1]) <= eps:
                cluster.append(p)
            else:
                clusters.append(cluster)
                cluster = []

        if cluster:       
            clusters.append(cluster)

        return clusters

    def partition(self, array, window_size=100, noise_tolerance=1, special=-1):
        """
        通过检测连续相同的值对array进行分区，当相同的值连续出现超过window_size次时，这些值将被划成一个区域
        """
        partitions = []
        observing = {}

        special_begin = None
        special_latest = None
        for index, value in enumerate(array):
            # 特殊值不做处理
            if value == special:
                special_latest = index
                if not special_begin:
                    special_begin = index
                continue

            # 处理观察值
            for key in observing:
                if value != int(key):
                    # 记录噪声的下标位置
                    observing[key]['noise_pos'].append(index)

                    if len(observing[key]['noise_pos']) > noise_tolerance:
                        if index - observing[key]['beginning'] >= window_size:
                            # 如果噪声的值的数量超过 noise_tolerance 且当前窗口长度 >= window_size, 则认为检测到一个区域
                            partitions.append((observing[key]['beginning'], index))

                            # 删除该观察值
                            del observing[key]
                        else:
                            # 向前移动观察值的窗口
                            next = None
                            for i in xrange(len(observing[key]['noise_pos']) - 1):
                                if observing[key]['noise_pos'][i] + 1 == observing[key]['noise_pos'][i + 1]:
                                    continue
                                else:
                                    next = observing[key]['noise_pos'][i] + 1
                                    break
                            if next:
                                observing[key]['beginning'] = next
                            else:
                                del observing[key]

            # 加入新观察值
            if not observing.has_key(str(value)):
                observing[str[value]] = {
                    'noise_pos': [],
                    'beginning': special_begin if special_latest == index - 1 else index
                }

            special_begin = special_latest = None
        return partitions


# Parameter eps
def merge(points, eps=5, window_size=100, representative='center'):
    points.sort()

    refined_points = []
    cluster = []

    def represent():
        if representative == 'center':
            return int(sum(cluster) / len(cluster))
        elif representative == 'left':
            return cluster[0]
        elif representative == 'right':
            return cluster[-1]
        else:
            raise 'unsupported representative'

    for p in points:
        if refined_points and p - refined_points[-1] < window_size:
            continue
        if not cluster or abs(p - cluster[-1]) <= eps:
            cluster.append(p)
        else:
            refined_points.append(represent())
            if p - refined_points[-1] < window_size:
                cluster = []
            else:
                cluster = [p]
    if cluster:
        refined_points.append(represent())

    return refined_points









def save_table(table, filepath):
    with open(filepath, 'w') as f:
        (a, b, c) = table.shape
        for i in xrange(a):
            for j in xrange(b):
                f.writelines([str(v) for v in table[i][j]])
                f.write('\n')



if __name__ == '__main__':
    import os
    base_dir = r'loan_logs/mixed_logs'
    filename = r'0.cm_300.re_450.re_650.lp_1100.lp_1200.cd_1450.re_1800.cm_1900.RIO_2250.cf_.mxml'
    path = os.path.join(base_dir, filename)
