# encoding: utf-8
import mxml
import os
import random

loan_log_base_dir = r'loan_logs'

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


def extract_loan_logs(name):
    """
    从已有的混合的日志中提取出每个模型独立的日志
    """
    if name == 'original':
        filepath = os.path.join(loan_log_base_dir, r'cb\cb5k.mxml')
        begin, end = 0, 500

    else:
        filepath = os.path.join(loan_log_base_dir, r'%s\%s5k.mxml' % (name, name))
        begin, end = 500, 1000

    log = mxml.parse(filepath)
    all_traces = set()
    for i in xrange(begin, end):
        all_traces.add(','.join(log['traces'][i]))

    dest_file = os.path.join(loan_log_base_dir, 'individual_logs\%s.txt' % name)
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



def generate_mixed_logs():
    models = ['original',
              'cb', 'cd', 'cf', 'cm', 'cp', 'fr',
              'lp', 'pl', 'pm', 're', 'rp', 'sw',
              'IOR', 'IRO', 'ORI','OIR','RIO','ROI']
    logs = {}
    for model in models:
        logs[model] = []
        for line in open(os.path.join(loan_log_base_dir, 'individual_logs\%s.txt' % model), 'r'):
            line = line.strip()
            if line:
                logs[model].append(line.split(','))

    log_count = 1
    model_count = 6
    log_len_choices = range(300, 3000, 600)

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
        sum = 0
        for item in config:
            filename += "%d.%s_" % (sum, item['name'])
            sum += item['length']
        filename += '.mxml'
        filepath = os.path.join(loan_log_base_dir, 'mixed_logs', filename)
        mxml.write(mixed_traces, filepath)



if __name__ == '__main__':
    # models = ['original',
    #           'cb', 'cd', 'cf', 'cm', 'cp', 'fr',
    #           'lp', 'pl', 'pm', 're', 'rp', 'sw',
    #           'IOR', 'IRO', 'ORI','OIR','RIO','ROI']
    # for model in models:
    #     extract(model)

    # for line in open('test.txt'):
    #     print line,
    generate_mixed_logs()

