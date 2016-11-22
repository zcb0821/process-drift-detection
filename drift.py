import mxml
import numpy as np
import matplotlib.pyplot as plt

MIN_WINDOW_SIZE = 100
NOISE_TOLERANCE = 1

def detect(filepath):
    # read log from mxml file
    print 'parsing %s' % filepath
    log = mxml.parse(filepath)

    # generate tar table
    print 'generating tar table'
    table = get_follow_table(log)

    # split each tar relation stream
    print 'splitting'
    left_points = []
    right_points = []
    with open(filepath.replace('mxml', 'table'), 'w') as f:
        for r, stream in table.iteritems():
            f.writelines([str(v) + ' ' for v in stream])
            f.writelines('\n')

            ranges = partition(stream)
            for range in ranges:
                left_points.append(range[0])
                right_points.append(range[1])

    # refine ranges
    print 'refining'
    points_1 = dbscan(left_points + right_points)

    refine_left_points = dbscan(left_points, representative='right')
    refine_right_points = dbscan(right_points, representative='left')
    points_2 = dbscan(refine_left_points + refine_right_points)

    print points_1
    print points_2



# Parameter eps
def dbscan(points, eps=5, representative='center'):
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
        if refined_points and p - refined_points[-1] < MIN_WINDOW_SIZE:
            continue
        if not cluster or abs(p - cluster[-1]) <= eps:
            cluster.append(p)
        else:
            refined_points.append(represent())
            if p - refined_points[-1] < MIN_WINDOW_SIZE:
                cluster = []
            else:
                cluster = [p]
    if cluster:
        refined_points.append(represent())

    return refined_points

def partition(array):
    detected = False
    result = []

    anchors = []
    window_beginning = 0
    for index, element in enumerate(stream):
        # add anchor
        if element != 0:
            anchors.append(index)
            if len(anchors) > NOISE_TOLERANCE:
                if index - window_beginning >= MIN_WINDOW_SIZE:
                    # detected
                    result.append((window_beginning, index))
                    # print '(%d, %d)' % (window_beginning, index),

                    if NOISE_TOLERANCE > 0:
                        window_beginning = index
                        anchors = [index]
                    else:
                        window_beginning = index + 1
                        anchors = []
                    detected = True
                else:
                    # move window ahead
                    window_beginning = anchors[0] + 1
                    anchors.pop(0)
    if detected:
        #print
        pass
    return result


def get_follow_table(log):
    log_len = len(log['traces'])

    table = {}
    for trace_idx, t in enumerate(log['traces']):
        # iterate each trace in reversed order
        for i in xrange(len(t) - 1, 0, -1):
            # adjacent follow relation
            # key = '%s-%s' % (t[i-1], t[i])
            # tar_flags = table.setdefault(key, np.zeros(log_len, np.uint8))
            # tar_flags[trace_idx] = 1

            # simple follow relation
            for j in xrange(i-1, 0, -1):
                key = '%s--%s' % (t[j], t[i])
                follow_stream = table.setdefault(key, np.zeros(log_len, np.uint8))
                follow_stream[trace_idx] = 1



    return table


def save_table(table, filepath):
    with open(filepath, 'w') as f:
        (a, b, c) = table.shape
        for i in xrange(a):
            for j in xrange(b):
                f.writelines([str(v) for v in table[i][j]])
                f.write('\n')


def map_event_to_idx(events):
    """
    give each event in events a unique id
    :param events: a set containing events (string type)
    :return: a dict in which the key is event name and the value is event id
    """
    index = 0
    event_idx = {}
    for event in events:
        event_idx.setdefault(event, index)
        index += 1
    return event_idx


if __name__ == '__main__':
    import os
    base_dir = r'loan_logs/mixed_logs'
    filename = r'0.cm_300.re_450.re_650.lp_1100.lp_1200.cd_1450.re_1800.cm_1900.RIO_2250.cf_.mxml'
    path = os.path.join(base_dir, filename)
    detect(path)
