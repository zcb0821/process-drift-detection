# encoding: utf-8
def partition(stream, min_len=100, noise_tolerance=0, ignore_value=-1):
    """
    通过检测连续相同的值对 array 进行分区，当相同的值连续出现超过 min_len 次时，这些值将被划成一个区域
    """
    intervals = []
    observing = {}

    ignore_begin, ignore_end = None, None
    for index, value in enumerate(stream):
        # 特殊值不做处理
        if value == ignore_value:
            ignore_end = index
            if ignore_begin is None:
                ignore_begin = index
            continue

        # 处理观察值
        deleted_keys = []
        for key in observing:
            if value != observing[key]['value']:
                # 记录噪声的下标位置
                observing[key]['noise_pos'].append(index)

                if len(observing[key]['noise_pos']) > noise_tolerance:
                    if index - observing[key]['beginning'] >= min_len:
                        # 如果噪声的值的数量超过 noise_tolerance 且当前窗口长度 >= window_size, 则认为检测到一个区域
                        intervals.append((observing[key]['beginning'], index))

                        # 标记删除该观察值
                        deleted_keys.append(key)
                    else:
                        # 向前移动观察值的窗口
                        next_beginning = None
                        for i in xrange(len(observing[key]['noise_pos']) - 1):
                            if observing[key]['noise_pos'][i] + 1 == observing[key]['noise_pos'][i + 1]:
                                continue
                            else:
                                next_beginning = observing[key]['noise_pos'][i] + 1
                                observing[key]['noise_pos'] = observing[key]['noise_pos'][i + 1:]
                                break
                        if next_beginning:
                            observing[key]['beginning'] = next_beginning
                        else:
                            deleted_keys.append(key)
                            observing[key] = None

        for key in deleted_keys:
            del observing[key]

        # 加入新观察值
        if observing.get(str(value)) is None:
            observing[str(value)] = {
                'noise_pos': [],
                'beginning': ignore_begin if ignore_end == index - 1 else index,
                'value': value
            }

        ignore_begin = ignore_end = None

    for key in observing:
        if len(stream) - observing[key]['beginning'] >= min_len:
            intervals.append((observing[key]['beginning'], len(stream)))
    return intervals


def partition_2(stream, min_len=100, ignore_value=-1):
    """
    通过检测连续相同的值对 array 进行分区，当相同的值连续出现超过 min_len 次时，这些值将被划成一个区域
    """
    intervals = []

    observing_value, observing_begin = None, None
    ignore_begin, ignore_end = None, None

    for index, value in enumerate(stream):
        # 特殊值不做处理
        if value == ignore_value:
            if ignore_begin is None:
                ignore_begin = index
            ignore_end = index
            continue

        if value != observing_value:
            if observing_value is not None and index - observing_begin >= min_len:
                # 如果噪声的值的数量超过 noise_tolerance 且当前窗口长度 >= window_size, 则认为检测到一个区域
                intervals.append((observing_begin, index))
            observing_value, observing_begin = None, None

        if observing_value is None:
            observing_value = value
            observing_begin = ignore_begin if ignore_end == index - 1 else index

        ignore_begin = ignore_end = None

    if observing_value is not None and len(stream) - observing_begin >= min_len:
        intervals.append((observing_begin, len(stream)))

    return intervals
