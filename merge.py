# encoding: utf-8
import Queue
def _cluster(points, eps=5):
    points.sort()

    clusters = []
    cluster = []

    for p in points:
        if not cluster or abs(p - cluster[-1]) <= eps:
            cluster.append(p)
        else:
            clusters.append(cluster)
            cluster = [p]

    if cluster:
        clusters.append(cluster)

    return clusters


def merge_1(intervals, enable_compatible=True, min_len=100):
    left_points, right_points = [], []

    for interval in intervals:
        left_points.append(interval[0])
        right_points.append(interval[1])

    if enable_compatible:
        left_clusters = _cluster(left_points)
        right_clusters = _cluster(right_points)

        refined_left_points = [cluster[-1] for cluster in left_clusters]
        refined_right_points = [cluster[0] for cluster in right_clusters]

        clusters = _cluster(refined_left_points + refined_right_points)
    else:
        clusters = _cluster(left_points + right_points)

    result = [0]
    for cluster in clusters:
        center = int(sum(cluster) / len(cluster))
        if center - result[-1] >= min_len:
            result.append(center)
    return result


def merge_2(intervals, total_range, min_len):
    print intervals
    points = []
    for interval in intervals:
        left_p, right_p = {'value': interval[0], 'isLeft': True}, \
                          {'value': interval[1], 'isLeft': False}
        left_p['right'], right_p['left'] = right_p, left_p
        # points.append(left_p)
        points.append(right_p)

    points.sort(key=lambda x: (x['value'], -x['left']['value']))

    partitioned = [total_range[0]]
    adapt_direction = [0]  # -1表示左移， 0表示不可移动， 1表示右移
    last_remain = 0
    # head_p = None
    # tail_p = None
    for p in points:
        if p['isLeft']:
            continue
            # if tail_p is None:
            #     head_p = tail_p = p
            # else:
            #     tail_p['next'] = p
            #     p['prev'] = tail_p
            #     tail_p = p
        else:
            left, right = p['left']['value'], p['value']
            if left <= partitioned[-1]:
                lack = max(0, min_len - (right - partitioned[-1]))
                remain = min(last_remain, partitioned[-1] - left)
                if lack < min_len * 0.5 and lack <= remain:
                    partitioned[-1] -= lack
                    partitioned.append(right)
                    adapt_direction.append(-1)
                    last_remain = min(min_len, partitioned[-1] - partitioned[-2] - min_len)
                else:
                    pass
                for i in xrange(len(partitioned)):
                    if partitioned[i] <= left:
                        continue
                    # prev_remain = 0 if adapt_direction[i - 1] >= 0 else partitioned[i - 1] - partitioned[i - 2]
                    # next_remain = 0 if adapt_direction[i] <= 0 else partitioned[i + 1] - partitioned[i]

                    if partitioned[i] - partitioned[i - 1] >= 2 * min_len \
                            and left - partitioned[i - 1] > min_len * 0.5 \
                            and partitioned[i] - left >= min_len:
                        partitioned.insert(i, max(left, partitioned[i - 1] + min_len))
                        adapt_direction.insert(i, 1)
                        break
            else:
                len_1 = left - partitioned[-1]
                len_2 = right - left
                next_remain = min(min_len, len_2 - min_len)
                len_1_lack = max(0, min_len - len_1)
                if last_remain + next_remain >= len_1_lack:
                    prev_borrow = int(len_1_lack * (last_remain / float(last_remain + next_remain)))
                    next_borrow = len_1_lack - prev_borrow
                    if prev_borrow > last_remain:
                        prev_borrow = last_remain
                        next_borrow = len_1_lack - prev_borrow
                    elif next_borrow > next_remain:
                        next_borrow = next_remain
                        prev_borrow = len_1_lack - next_borrow
                    partitioned[-1] -= prev_borrow
                    partitioned.append(left + next_borrow)
                    adapt_direction.append(1)
                    partitioned.append(right)
                    adapt_direction.append(-1)
                    last_remain = min(min_len, partitioned[-1] - partitioned[-2] - min_len)
                else:
                    pass

    if partitioned[-1] != total_range[-1]:
        lack = max(0, min_len - (total_range[-1] - partitioned[-1]))
        if lack <= last_remain:
            partitioned[-1] = partitioned[-1] - lack
            partitioned.append(total_range[-1])
        else:
            partitioned[-1] = total_range[-1]
    return partitioned

def dbscan_1d(array, radius, min_pts):
    X = sorted(array)
    l = len(X)

    C = [0] * l
    R = range(l)

    for i in xrange(l - 1):
        for j in xrange(i + 1, l):
            if abs(X[i] - X[j]) <= radius:
                C[i] += 1
                C[j] += 1
                R[i] = j
            else:
                break

    clusters = []
    cluster = []
    right = -1
    for i in xrange(l):
        cluster.append(X[i])
        if C[i] >= min_pts and R[i] > right:
            right = R[i]
        if i == R[i]:
            clusters.append(cluster)
            cluster = []
            right = -1

    return clusters


def merge_by_dbscan(intervals, total_range, min_len, radius, min_pts, alpha=0.9):
    array = list()
    for x, y in intervals:
        array.append(x)
        array.append(y)

    clusters = dbscan_1d(array, radius, min_pts)
    clusters.sort(key=lambda x: -len(x))
    partitioned = [total_range[0], total_range[-1]]
    for cluster in clusters:
        center = sum(cluster) / len(cluster)
        for i in xrange(len(partitioned)):
            if partitioned[i] > center:
                if partitioned[i] - partitioned[i-1] >= 2 * min_len:
                    left, right = center - partitioned[i-1], partitioned[i] - center
                    if min_len * alpha <= left <= min_len:
                        partitioned.insert(i, partitioned[i-1] + min_len)
                    elif min_len * alpha <= right <= min_len:
                        partitioned.insert(i, partitioned[i] - min_len)
                    elif left >= min_len and right >= min_len:
                        partitioned.insert(i, center)
    return partitioned

def _test_dbscan_1d():
    array = [1, 2, 3, 12, 13, 15, 23, 34, 35, 36]
    clusters = dbscan_1d(array, 2, 2)

    def print_clusters():
        for cluster in clusters:
            for v in cluster:
                print v,
            print ', ',
    print_clusters()

if __name__ == '__main__':
    intervals = [(0, 1761), (0, 122), (659, 2118), (0, 660), (0, 526), (1994, 2118), (258, 1643), (1755, 2118), (658, 2118), (1524, 2118), (257, 1639), (0, 259), (1754, 2118), (659, 1525), (519, 660), (383, 2118), (524, 660), (0, 661), (1638, 2118), (1991, 2118), (0, 664), (1518, 1639), (374, 2118), (1525, 2118), (658, 1527), (0, 662), (0, 1525), (0, 111), (1977, 2118), (0, 524), (1524, 1642), (0, 261), (1993, 2118), (524, 662), (0, 1756), (1523, 2118), (0, 659), (1522, 2118), (0, 265), (523, 665), (0, 1757)]
    min_len = 100
    total_range = (0, 2473)
    print merge_by_dbscan(intervals, total_range, min_len, min_len * 0.05, 2)
    # _test_dbscan_1d()
