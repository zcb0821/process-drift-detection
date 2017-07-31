# encoding: utf-8
import log
import mxml
import os
import detector
import json
import time
import subprocess
import re
import evaluation
from matplotlib import pyplot
import birelations
import numpy as np

log_dir = r'./experiments/logs'
result_dir = r'./experiments/result'

################################################################
# 公共部分
################################################################
def parse_title(s):
    pattern = re.compile(r'^\[(\d+)\s(\d+)\]$')
    match = pattern.match(s)
    return int(match.group(1)), int(match.group(2))

def parse_log_filename(filename):
    s1, s2 = filename.rstrip(".mxml").split('-')
    num_model, num_trace = parse_title(s1)
    label = eval(s2)
    return label, num_model, num_trace

################################################################


def generate_logs(dataset):
    model_counts = [2, 4, 6, 8, 10, 12, 14, 16]
    trace_ranges = [(200, 300), (450, 550), (700, 800), (950, 1050)]

    individual_logs = log.read_individual_log(dataset)
    for model_count in model_counts:
        for min_n, max_n in trace_ranges:
            traces, config = log.random_mix(individual_logs, num=model_count, min_n=min_n, max_n=max_n)
            filename = '[%d %d]-' % (model_count, (min_n + max_n) / 2) + str(log.label_of_config(config)) + '.mxml'
            print filename
            filepath = os.path.join(log_dir, filename)
            mxml.write(traces, filepath)


def online_detect(min_len=100, window_size=5, sensibility=3):
    results = []
    for filename in os.listdir(log_dir):
        r = {}
        s1, s2 = filename.rstrip(".mxml").split('-')
        r['label'] = eval(s2)
        r['title'] = s1
        d = detector.OnlineDetector(min_len=100)
        d.sensibility = sensibility
        d.window_size = window_size
        r['result'], r['delay'] = d.detect(mxml.parse(os.path.join(log_dir, filename))['traces'])
        results.append(r)
        print '-----------------'
        print filename
        print r['label']
        print r['result']
    filename = '%s-%d-%d-%d.json' % ('online', min_len, window_size, sensibility)
    with open(os.path.join(result_dir, filename), 'w') as f:
        f.write(json.dumps(results))


def offline_detect(min_len=100):
    results = []
    for filename in os.listdir(log_dir):
        r = {}
        s1, s2 = filename.rstrip(".mxml").split('-')
        r['label'] = eval(s2)
        r['title'] = s1
        d = detector.DriftDetector()
        d.min_pts = 1
        r['result'] = d.detect(mxml.parse(os.path.join(log_dir, filename))['traces'])
        results.append(r)
        print '-----------------'
        print filename
        print r['label']
        print r['result']
    filename = '%s-%d-%d-%d.json' % ('offline', d.min_len, d.radius, d.min_pts)
    with open(os.path.join(result_dir, filename), 'w') as f:
        f.write(json.dumps(results))




def prodrift_detect(window_size, fixed=False):
    results = []
    for filename in os.listdir(log_dir):
        r = {}
        results.append(r)
        s1, s2 = filename.rstrip(".mxml").split('-')
        r['label'] = eval(s2)
        r['title'] = s1
        r['result'], time = single_prodrift_detect(os.path.abspath(os.path.join(log_dir, filename)), window_size)

    filename = '%s-%d%s.json' % ('prodrift', window_size, "fixed")
    with open(os.path.join(result_dir, filename), 'w') as f:
        f.write(json.dumps(results))

def time_measure_prodrift():
    window_size = 100
    parse_table = np.zeros((4, 8))
    detect_table = np.zeros((4, 8))
    for filename in os.listdir(log_dir):
        _, time = single_prodrift_detect(os.path.abspath(os.path.join(log_dir, filename)), window_size)
        _, n, s = parse_log_filename(filename)
        i, j = s / 250 - 1, n / 2 - 1
        parse_table[i][j] = time[0]
        detect_table[i][j] = time[1]

    def print_table(table):
        n, m = table.shape
        for i in xrange(n):
            for j in xrange(m):
                print table[i][j],
                if j != m - 1:
                    print ',',
                else:
                    print
        print
    print_table(parse_table)
    print_table(detect_table)



def single_prodrift_detect(log_path, window_size, slide="-fwin"):
    class_path = r"E:\BPM\QUT 2016 - Fast and Accurate Business Process Drift Detection\prodrift\bin"
    cmd = 'java -cp "%s" ee.ut.eventstr.main.Main "%s" runs %d %s' % (class_path, log_path, window_size, slide)
    print log_path
    o_text = subprocess.check_output(cmd, shell=True)
    pattern = re.compile(r'run: (\d+)')
    result = [int(i) for i in pattern.findall(o_text)]
    time = [float(i) / 1e9 for i in re.compile(r"time: (\d+)").findall(o_text)]
    return result, time



def f1_score(f, precision_criterions):
    results = json.load(open(f))
    scores = []

    for pc in precision_criterions:
        scores.append(0)
        for r in results:
            num_model, len_model = parse_title(r['title'])
            _, _, score, _, _ = evaluation.evaluate_by_label(r['label'], r['result'], len_model*pc)
            scores[-1] += score
        scores[-1] /= len(results)
    return scores


def plot_of_fs(c, l):
    results = json.load(open(os.path.join(result_dir, 'offline-min_len-0-2.json')))
    for r in results:
        if r['model_count'] == c and r['single_length'] == l:
            XY =[]
            for key, value in r['result'].iteritems():
                print key, value
                _, _, score, _, _ = evaluation.evaluate_by_label(r['label'], value, 10)
                XY.append((int(key), score))

    XY.sort(key=lambda x: x[0])
    X = [i[0] for i in XY]
    Y = [i[1] for i in XY]
    pyplot.title('model count: %d, log size of each model: %d, tolerance: 10' % (c, l))
    pyplot.plot(X, Y, 'b')
    pyplot.plot(X, Y, 'bo')
    pyplot.xticks(X)
    pyplot.yticks([i / 10.0 for i in xrange(0, 12, 1)])
    pyplot.xlabel('mininum size')
    pyplot.ylabel('f-score')
    pyplot.show()

##############################################################
# 最小长度实验开始
# 1.遍历所有日志，每个日志用不同的 min_len 进行检测
# 2.保存所有结果到一个文件中
# min_len的选择：
#   1. 固定：[100, 200, 300, 400, 500, 600, 700, 900, 1000, 1100]
#   2. 合适比例：比如500规模的日志从[50, 100, 150, ..., 600]
#      range(500/10, 500 + 500/10 * 2 + 1, 500/10)
# 其他参数配置：
#   radius = 10，
# 保存结果格式：
#     {
#         "n_model": 10,
#         "n_traces": 500,
#         "label": [],
#         "results": [(50, []), (100, [])]
#     }
def run_results_with_different_min_len(fixed=True, radius=10):
    results = []
    # 遍历所有 log
    for filename in os.listdir(log_dir):
        label, n, m = parse_log_filename(filename)
        # # 找到对应的log
        # if n != num_model or m != num_traces:
        #     continue
        result = {
            'label': label,
            "n_model": n,
            "n_traces": m,
            "results": []
        }
        # 遍历 min_len 选项
        if fixed:
            list_min_len = range(100, 1001, 100)
        else:
            step = m / 10
            list_min_len = range(step, m + step * 2 + 1, step)
        for min_len in list_min_len:
            d = detector.DriftDetector(min_len, radius)
            d.r_types = [(birelations.weak_causal, 'all')]
            changes = d.detect(os.path.join(log_dir, filename))
            print min_len, changes
            result['results'].append((min_len, changes))
        results.append(result)
    filename = '[最小长度实验]-[方法%s-BP]-[半径%d]-[%s].json' % ('offline', radius, 'fixed' if fixed else 'adap')
    with open(os.path.join(result_dir, filename.decode('utf-8')), 'w') as f:
        f.write(json.dumps(results))


##############################################################
# 聚类半径实验开始
# 1.遍历所有日志，每个日志用固定100的最小长度进行检测，但聚类半径从 2 到 100
# 2.保存所有结果到一个文件中
# 保存结果格式：
#     {
#         "n_model": 10,
#         "n_traces": 500,
#         "label": [],
#         "results": [(2, []), (100, [])]
#     }

def run_result_with_different_radius(list_radius, min_len=400, num_model=10, num_traces=500):
    results = []
    # 遍历所有 log
    for filename in os.listdir(log_dir):
        label, n, m = parse_log_filename(filename)
        # 找到对应的log
        if n != num_model or m != num_traces:
            continue
        result = {
            'label': label,
            "n_model": n,
            "n_traces": m,
            "results": []
        }
        for radius in list_radius:
            d = detector.DriftDetector(min_len, radius)
            changes = d.detect(os.path.join(log_dir, filename))
            print radius, changes
            result['results'].append((radius, changes))
        results.append(result)
        break
    filename = '[聚类半径实验]-[方法%s]-[MINLEN%d]-[日志%d,%d].json' % ('offline', min_len, num_model, num_traces)
    with open(os.path.join(result_dir, filename.decode('utf-8')), 'w') as f:
        f.write(json.dumps(results[0]))

##############################################################
if __name__ == "__main__":
    # run_results_with_different_min_len()
    # run_results_with_different_min_len(False)
    # for i in xrange(250, 1001, 250):
    #     run_result_with_different_radius(range(100, 1101, 100), min_len=100, num_model=10, num_traces=i)
    # prodrift_detect(100, True)

    # log_path = os.path.abspath(r"./experiments/logs/[16 250]-[0, 266, 565, 803, 1031, 1297, 1552, 1754, 1955, 2188, 2439, 2736, 3023, 3226, 3446, 3664, 3894].mxml")
    # print single_prodrift_detect(log_path, 100)

    time_measure_prodrift()