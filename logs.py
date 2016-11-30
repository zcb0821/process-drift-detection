# encoding: utf-8
import mxml
import os
import random

individual_logs_dir = r'./individual_logs'
mixed_logs_dir = r'./mixed_logs'

loan_log_dir = os.path.join(individual_logs_dir, 'loan')

def is_trace_equal(t1, t2):
    """
    判断两条 trace 是否相等
    """
    if len(t1) != len(t2):
        return False
    for i in xrange(len(t1)):
        if t1 != t2:
            return False
    return True


def extract_loan_logs(name, dataset_path):
    """
    从 QUT 2016 - Fast and Accurate Business Process Drift Detection
    的数据集中提取出每个模型独立的日志
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


def mix(logs, config):
    """
    混合不同模型产生的日志，logs 是不同模型的集合，config 是混合的配置
    e.g. log = {
            model-name: [trace1, trace2,...]
        }
        config = [{
            'name': name of model, like '
            'length': length of model
        }]
    """
    mixed_traces = []
    for item in config:
        traces = logs[item['name']]
        for i in xrange(item['length']):
            index = random.randint(0, len(traces)-1)
            mixed_traces.append(traces[index])
    return mixed_traces


def generate_mixed_logs(dataset, model_count=5, trace_range=(100, 300), trace_step=50, log_count=1):
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

    log_len_choices = range(trace_range[0], trace_range[1], trace_step)

    configs = [[] for i in xrange(log_count)]
    for i in xrange(log_count):
        for j in xrange(model_count):
            model = models[random.randint(0, len(models)-1)]
            length = random.choice(log_len_choices)
            configs[i].append({
                'name': model,
                'length': length
            })

    for config in configs:
        mixed_traces = mix(logs, config)
        filename = ''
        trace_sum = 0
        for item in config:
            filename += "%d.%s_" % (trace_sum, item['name'])
            trace_sum += item['length']
        filename += '.mxml'
        filepath = os.path.join(mixed_logs_dir, filename)
        mxml.write(mixed_traces, filepath)



if __name__ == '__main__':
    generate_mixed_logs()

