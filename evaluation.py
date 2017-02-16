# encoding: utf-8

def evaluate_by_label(label, result, thelta):
    TP = []
    FP = []
    FN = []
    TP_flags = [False] * len(result)
    for i, l in enumerate(label):
        closest_distance, closest_index = None, None
        for j, r in enumerate(result):
            if abs(r - l) <= thelta and not TP_flags[j] and (closest_distance is None or abs(r - l) < closest_distance):
                closest_distance, closest_index = abs(r - l), j
            if j > 0 and abs(r - l) >= thelta and abs(r - l) > abs(result[j - 1] - l):
                break
        if closest_index is not None:
            TP.append((l, result[closest_index], closest_distance))
            TP_flags[closest_index] = True
        else:
            FN.append(l)
    for i, flag in enumerate(TP_flags):
        if not flag:
            FP.append(result[i])

    recall = float(len(TP)) / len(label)
    precision = float(len(TP)) / len(result)
    f1_score = 2 * precision * recall / (precision + recall)
    TP_error = float(sum([t[-1] for t in TP])) / len(TP)
    return recall, precision, f1_score, TP_error

def _test_evaluate_by_label():
    label = [0, 111, 258, 385, 524, 659, 1525, 1639, 1756, 1995, 2118]
    result = [0, 111, 259, 383, 524, 659, 1525, 1639, 1756, 1856, 1993, 2118]
    print evaluate_by_label(label, result, 10)

if __name__ == '__main__':
    _test_evaluate_by_label()