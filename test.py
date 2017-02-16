from drift import DriftDetector
import log
import birelations


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

        if len(result) <\
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


def random_test(dataset, r_types, model_count = 6, times=100, console_output=False):
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


if __name__ == '__main__':
    # loan_individual_logs = read_models('group-A')
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
    # s = find_failure_cases('group-A', [(birelations.direct_causal, 'all'), (birelations.co_exist, 'first')], console_output=True, times=500)
    s = random_test('my-loan', [(birelations.direct_causal, 'all'), (birelations.co_exist, 'first')], model_count=2,  console_output=True, times=20)
    print_bi_tuple_set(s)