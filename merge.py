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
    """
    按照右端点从小到大对区间进行排序。对于右端点相同的两个区间，左端点大的排前，小的排后。
    顺序遍历排序后的每个区间进行整合划分。
    """
    # print intervals
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

    for i in xrange(l):
        for j in xrange(i + 1, l):
            if X[i] == X[j]:
                C[i] = min_pts
                R[i] = j
                break
            if abs(X[i] - X[j]) <= radius:
                C[i] += 1
                C[j] += 1
                R[i] = j
            else:
                break

    clusters = []
    cluster = []
    right = 0
    for i in xrange(l):
        cluster.append(X[i])
        if C[i] >= min_pts and R[i] > right:
            right = R[i]
        if i == right:
            clusters.append(cluster)
            cluster = []
            right = i + 1

    return clusters


def merge_by_dbscan(intervals, total_range, min_len, radius, min_pts, alpha=0.9):
    # print intervals
    array = list()
    for x, y in intervals:
        array.append(x)
        array.append(y)

    # 对所有分割点进行密度聚类
    clusters = dbscan_1d(array, radius, min_pts)
    # print clusters

    # 按照簇的规模从大到小对簇进行排序
    clusters.sort(key=lambda x: -len(x))
    # print clusters

    # 初始化分割结果为整个区间
    partitioned = [total_range[0], total_range[-1]]

    # 顺序遍历排序后的聚类簇
    for cluster in clusters:
        # 采用中心点代表整个簇
        # TODO: 可以尝试其他代表点，如左端点或右端点
        center = sum(cluster) / len(cluster)

        # 决定中心点的插入位置
        for i in xrange(len(partitioned)):
            if partitioned[i] > center:
                if partitioned[i] - partitioned[i - 1] >= 2 * min_len:
                    left, right = center - partitioned[i - 1], partitioned[i] - center
                    if min_len * alpha <= left <= min_len:
                        partitioned.insert(i, partitioned[i - 1] + min_len)
                    elif min_len * alpha <= right <= min_len:
                        partitioned.insert(i, partitioned[i] - min_len)
                    elif left >= min_len and right >= min_len:
                        partitioned.insert(i, center)
            elif partitioned[i] == center:
                break
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
    intervals = [(23040, 32001), (23053, 32001), (23052, 32001), (23049, 32001), (0, 23059), (13414, 14649),
                 (23055, 32001), (23056, 32001), (0, 32001), (23054, 32001), (23045, 32001)]
    min_len = 100
    total_range = (0, 2473)
    print merge_by_dbscan(intervals, total_range, min_len, min_len * 0.05, 2)
    # _test_dbscan_1d()
