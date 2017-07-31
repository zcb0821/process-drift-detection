# encoding: utf-8
import mxml
import os
import random

individual_logs_dir = r'./individual_logs'
mixed_logs_dir = r'./mixed_logs'

loan_log_dir = os.path.join(individual_logs_dir, 'loan')


def extract_loan_logs(name, dataset_path):
    """
    从论文 QUT 2016 - Fast and Accurate Business Process Drift Detection 的数据集中提取出每个模型独立的日志
    """
    if name == 'original':
        filepath = os.path.join(dataset_path, r'cb\cb5k.mxml')
        begin, end = 0, 500
    else:
        filepath = os.path.join(dataset_path, r'%s\%s5k.mxml' % (name, name))
        begin, end = 500, 1000

    log = mxml.parse(filepath)
    all_traces = set()
    for i in xrange(begin, end):
        all_traces.add(','.join(log['traces'][i]))

    dest_file = os.path.join(loan_log_dir, '%s.txt' % name)
    with open(dest_file, 'w') as f:
        for trace in all_traces:
            f.write(trace)
            f.write('\n')
    print 'write model: %s  length: %d' % (name, len(all_traces))


def _copy_log(log):
    new_log = [None] * len(log)
    for i in xrange(len(log)):
        new_log[i] = log[i][:]
    return new_log


def mix(logs, config):
    """
    混合不同模型产生的日志，logs 是不同模型的集合，config 是混合的配置
    log = {
        'model-name': [[a,b c],...]
    }
    config = [{
        'name': name of model, like '
        'length': length of model
    }]
    """
    mixed_traces = []
    for item in config:
        log = logs[item['name']]
        needed_log_length = item['length']
        # 当需要的 trace 数量大于日志大小时，保证日志的完整性
        if needed_log_length >= len(log):
            copy_of_log = _copy_log(log)
            random.shuffle(copy_of_log)
            mixed_traces.extend(copy_of_log)
            needed_log_length -= len(log)
        for i in xrange(needed_log_length):
            trace = random.choice(log)
            mixed_traces.append(trace[:])
    return mixed_traces


def read_individual_log(dataset):
    models = []
    logs = {}
    for filename in os.listdir(os.path.join(individual_logs_dir, dataset)):
        model, _ = os.path.splitext(filename)
        models.append(model)
        logs[model] = []
        for line in open(os.path.join(individual_logs_dir, dataset, filename), 'r'):
            line = line.strip()
            if line:
                logs[model].append(line.split(','))
    return logs


def random_mix(logs, num, min_n, max_n=None):
    config = []

    models = logs.keys()
    last_model = None
    for i in xrange(num):
        while True:
            # 保证相邻的模型不相同
            model = random.choice(models)
            if model != last_model:
                last_model = model
                break
        if max_n is None:
            length = random.randrange(max(min_n, len(logs[model])), int(max(min_n, len(logs[model])) * 1.5))
        else:
            length = random.randrange(min_n, max_n)
        config.append({
            'name': model,
            'length': length
        })

    mixed_traces = mix(logs, config)
    return mixed_traces, config


def label_of_config(config):
    label = [0]
    for item in config:
        label.append(label[-1] + item['length'])
    return label


def name_of_config(config):
    name = ''
    trace_sum = 0
    for item in config:
        s = item['name'].lstrip('model_')
        if not s:
            s = 'origin'
        name += "[%d %s]-" % (trace_sum, s)
        trace_sum += item['length']
    name += '[%d end]' % trace_sum
    return name


if __name__ == '__main__':
    pass
