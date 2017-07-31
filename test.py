from detector import DriftDetector, OnlineDetector
import log
import birelations
import mxml
import os


def find_failure_cases(dataset, r_types, times=500, console_output=False):
    failures = set()
    individual_logs = log.read_individual_log(dataset)
    for i in xrange(times):
        traces, config = log.random_mix(individual_logs, num=2, min_n=100)
        label = log.label_of_config(config)
        detector = DriftDetector()
        detector.r_types = r_types
        if console_output:
            print '----------------------------testing two models-----------------------------------'
            print 'dataset: %s,  model_1: %s,  model_2: %s' % (dataset, config[0]['name'], config[1]['name'])
            print 'relations:  ', r_types

        result = detector.detect(traces)
        if console_output:
            print 'label:  ', label
            print 'result: ', result

        if len(result) < \
                len(label):
            if config[0]['name'] < config[1]['name']:
                failures.add((config[0]['name'], config[1]['name']))
            else:
                failures.add((config[1]['name'], config[0]['name']))
    return failures


def test_two_models(dataset, model_1, model_2, r_types, console_output=True):
    if console_output:
        print '----------------------------testing two models-----------------------------------'
        print 'dataset: %s,  model_1: %s,  model_2: %s' % (dataset, model_1, model_2)
        print 'relations:  ', r_types
    individual_logs = log.read_individual_log(dataset)
    model_1_trace_length = 500
    model_2_trace_length = 500
    config = [
        {
            'name': model_1,
            'length': model_1_trace_length
        },
        {
            'name': model_2,
            'length': model_2_trace_length
        }
    ]
    traces = log.mix(individual_logs, config)
    detector = DriftDetector()
    detector.r_types = r_types
    detector.console_output = True
    result = detector.detect(traces)
    if console_output:
        print '---------------'
        print 'label:  ', 0, model_1_trace_length, model_1_trace_length + model_2_trace_length
        print 'result: ', result
        if len(result) == 3:
            print 'successfully'
        print '---------------'
    return len(result) == 3


def random_test(dataset, r_types, model_count=6, times=100, console_output=False):
    failures = set()
    individual_logs = log.read_individual_log(dataset)
    for i in xrange(times):
        traces, config = log.random_mix(individual_logs, num=model_count, min_n=100)
        label = log.label_of_config(config)
        detector = DriftDetector()
        detector.min_len = 100
        detector.r_types = r_types
        if console_output:
            print '----------------------------testing two models-----------------------------------'
            print 'dataset: %s' % dataset
            print 'config: %s' % log.name_of_config(config)
            print 'relations:  ', r_types

        result = detector.detect(traces)
        if console_output:
            print 'label:  ', label
            print 'result: ', result

        if len(result) < len(label):
            if config[0]['name'] < config[1]['name']:
                failures.add((config[0]['name'], config[1]['name']))
            else:
                failures.add((config[1]['name'], config[0]['name']))
    return failures


def generate_mixed_log(dataset, model_count=10, min_n=100, times=1):
    individual_logs = log.read_individual_log(dataset)
    for i in xrange(times):
        traces, config = log.random_mix(individual_logs, num=model_count, min_n=min_n)
        filename = log.name_of_config(config) + '.mxml'
        filepath = os.path.join(log.mixed_logs_dir, dataset, filename)
        mxml.write(traces, filepath)


if __name__ == '__main__':
    # loan_individual_logs = read_models('simple')
    # for i in xrange(100):
    #     print i, '.---------------------------------------------'
    #     traces, label, config = random_mix(loan_individual_logs, model_num=2, trace_range=(150, 301), trace_step=50)
    #     detector = DriftDetector()
    #     detector.frequency_levels = ['all']
    #     detector.relations = [birelations.weak_causal]
    #     result = detector.detect(traces)
    #     if len(result) != len(label):
    #         print config
    #         print 'label:  ', label
    #         print 'result: ', result


    def print_bi_tuple_set(s):
        result = {}
        for item in s:
            x = result.setdefault(item[0], [])
            x.append(item[1])
        keys = sorted(result.keys())
        for key in keys:
            print '%s - [%s]' % (key, ', '.join(result[key]))


    # test_two_models('my-loan', 'model_rp', 'model_lp', [(birelations.direct_causal, 'all')])
    # s = find_failure_cases('simple', [(birelations.direct_causal, 'all'), (birelations.co_exist, 'first')], console_output=True, times=500)
    # s = random_test('my-loan', [(birelations.direct_causal, 'all'), (birelations.co_exist, 'first')], model_count=10,  console_output=True, times=20)
    # print_bi_tuple_set(s)
    # generate_mixed_log('simple', times=10)

    # individual_logs = log.read_individual_log("my-loan")
    # traces, config = log.random_mix(individual_logs, num=10, min_n=100)

    # traces = mxml.parse(r"./experiments/logs/[12 750]-[0, 793, 1518, 2282, 3078, 3819, 4539, 5250, 6027, 6759, 7504, 8238, 8947].mxml")['traces']
    # oldetector = OnlineDetector(100)
    # oldetector.sensibility = 3
    # oldetector.r_funcs = {
    #     # 'wc': birelations.weak_causal,
    #     'dc': birelations.direct_causal
    # }
    #
    # result = [0]
    # delay = [0]
    # for i, trace in enumerate(traces):
    #     change = oldetector.receive(trace)
    #     if change:
    #         result.append(change)
    #         delay.append(i)
    # print "\n", result
    # print delay
    #
    # ofdetector = DriftDetector()
    # ofdetector.min_len = 825
    # ofdetector.radius = 825 * 0.05
    # ofdetector.min_pts = 2
    # ofdetector.r_types = [
    #     (birelations.direct_causal, 'all'),
    #     # (birelations.weak_causal, 'all')
    # ]
    # result = ofdetector.detect(traces)
    # print result

    dd = DriftDetector(min_len=20)
    dd.detect("./experiments/logs/[12 1000]-[0, 987, 1945, 2977, 3990, 5008, 6030, 7016, 8001, 9003, 9957, 10928, 11936].mxml")
    dd.drawCandidates()
