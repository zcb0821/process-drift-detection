# encoding: utf-8
import json
import os

import matplotlib
from matplotlib import pyplot as plt

import evaluation
from detector import DriftDetector

log_dir = r'./logs'
result_dir = r'./result'

# matplotlib.rcParams.update({'font.family': 'STIXGeneral', 'mathtext.fontset': 'stix'})
matplotlib.defaultParams.update({'font.size': 14})
matplotlib.rcParams['hatch.linewidth'] = 0.8
matplotlib.rcParams['hatch.color'] = '#444444'
matplotlib.rcParams.update(
    {'font.family': 'Times New Roman', 'mathtext.fontset': 'stix'})


def plot_of_min_len():
    p = os.path.join(
        result_dir, '[最小长度实验]-[方法offline]-[半径10]-[fixed].json').decode('utf-8')
    results = json.load(open(p))
    samples = []
    for r in results:
        if r['n_model'] == 10:
            sample = {
                'n_traces': r['n_traces'],
                'n_model': r['n_model'],
                'X': [],
                'Y': []
            }
            r['results'].sort(key=lambda x: x[0])  # 按窗口长度排序
            for v in r['results']:
                _, _, score, _, _ = evaluation.evaluate_by_label(
                    r['label'], v[-1], 10)
                sample['X'].append(v[0])
                sample['Y'].append(score)
            samples.append(sample)

    samples.sort(key=lambda sample: sample['n_traces'])

    # 画成 2 * 2 的图
    # for i, Y in enumerate(YY):
    #     plt.subplot(220 + i + 1)
    #     plt.title("$L_{10, %d}$" % Y[0], {'fontsize': 12})
    #     plt.xlabel('Mininum Window Size', fontsize=12)
    #     plt.ylabel('F-score', fontsize=12)
    #     plt.bar(X, Y[-1], width=50, color='blue')
    #     plt.xticks(X, rotation=45, fontsize=10)
    #     plt.yticks(fontsize=10)
    #     plt.subplots_adjust(top=0.9, bottom=0.2, left=0.05, right=0.95, hspace=0.25,
    #                         wspace=0.35)
    #     # pyplot.plot(xi, yi)

    # 画成同一幅图
    colors = ['#81c2d6', '#8192d6', '#dcf7a1', '#d9b3b6']
    hatches = ['//', '--', 'xx', '..']
    bar_width = 18
    # x axis setting
    plt.xlim((0, 1200))
    plt.xticks(samples[0]['X'], fontsize=14)
    plt.xlabel("Minimum Window Size", fontsize=14)

    # y axis setting
    plt.ylabel('F-score', fontsize=14)
    plt.yticks(map(lambda x: x / 10.0, range(0, 11, 1)), fontsize=14)
    for i, sample in enumerate(samples):
        sample['X'] = map(lambda x: (x - bar_width / 2 * 3) +
                          bar_width * i, sample['X'])
        plt.bar(sample['X'], sample['Y'], width=bar_width, color="none", edgecolor='black', hatch=hatches[i],
                linewidth=0.8, label='$L_{%d, %d}$' % (sample['n_model'], sample['n_traces']))
    plt.legend(fontsize=14)
    plt.subplots_adjust(top=0.98, bottom=0.1, left=0.08,
                        right=0.96, hspace=0.25, wspace=0.35)
    plt.show()


def plot_of_radius():
    """
    聚类半径影响图
    """
    files = [
        '[聚类半径实验]-[方法offline]-[MINLEN100]-[日志10,250].json',
        '[聚类半径实验]-[方法offline]-[MINLEN100]-[日志10,500].json',
        '[聚类半径实验]-[方法offline]-[MINLEN100]-[日志10,750].json',
        '[聚类半径实验]-[方法offline]-[MINLEN100]-[日志10,1000].json'
    ]

    for i, f in enumerate(files):
        data = json.load(open(os.path.join(result_dir, f.decode('utf-8'))))
        XY = []
        for v in data['results']:
            _, _, score, _, _ = evaluation.evaluate_by_label(
                data['label'], v[-1], 10)
            XY.append((v[0], score))
        XY.sort(key=lambda x: x[0])
        X = [v[0] for v in XY]
        Y = [v[-1] for v in XY]
        plt.subplot(220 + i + 1)
        plt.title("$L_{10, %d}$" % (250 * (i + 1)), {'fontsize': 12})
        plt.xlabel('Radius of DBSCAN', {'fontsize': 12})
        plt.ylabel('F-score', {'fontsize': 12})
        plt.bar(X, Y, width=50, color="blue")
        plt.xticks(X, rotation=45, fontsize=10)
        plt.subplots_adjust(top=0.9, bottom=0.2, left=0.05, right=0.95, hspace=0.25,
                            wspace=0.35)
    plt.show()


def plot_of_radius_4_in_1(style='bar'):
    files = [
        '[聚类半径实验]-[方法offline]-[MINLEN100]-[日志10,250].json',
        '[聚类半径实验]-[方法offline]-[MINLEN100]-[日志10,500].json',
        '[聚类半径实验]-[方法offline]-[MINLEN100]-[日志10,750].json',
        '[聚类半径实验]-[方法offline]-[MINLEN100]-[日志10,1000].json'
    ]

    samples = []
    for i, f in enumerate(files):
        data = json.load(open(os.path.join(result_dir, f.decode('utf-8'))))
        sample = {'X': [], 'Y': [], 'n_model': data['n_model'],
                  'n_traces': data['n_traces']}
        XY = []
        for v in data['results']:
            _, _, score, _, _ = evaluation.evaluate_by_label(
                data['label'], v[-1], 10)
            XY.append((v[0], score))
        XY.sort(key=lambda x: x[0])
        sample['X'] = [v[0] for v in XY]
        sample['Y'] = [v[-1] for v in XY]
        samples.append(sample)
    # 画成同一幅图
    # colors = ['#FF6666', '#FFFF66', '#99CC66', '#996699']
    hatches = ['//', '--', 'xx', '..']
    bar_width = 20

    # 横坐标轴设置
    plt.xlim((0, 1200))
    plt.xticks(samples[0]['X'], fontsize=14)
    plt.xlabel("$eps$", fontsize=14)

    # 纵坐标轴设置
    plt.ylabel('F-score', fontsize=14)
    plt.yticks(map(lambda x: x / 10.0, range(0, 11, 1)), fontsize=14)
    for i, sample in enumerate(samples):
        if style == 'bar':
            sample['X'] = map(lambda x: (x - bar_width / 2 *
                                         3) + bar_width * i, sample['X'])
            plt.bar(sample['X'], sample['Y'], width=bar_width, color="none", edgecolor='black',
                    hatch=hatches[i], linewidth=0.8,
                    label='$L_{%d, %d}$' % (sample['n_model'], sample['n_traces']))
        else:
            plt.plot(sample['X'], sample['Y'], 'o-')
    plt.legend(fontsize=14)
    plt.subplots_adjust(top=0.98, bottom=0.15, left=0.08,
                        right=0.96, hspace=0.25, wspace=0.35)
    plt.show()


def f1_scores(f, precision_criterions):
    results = json.load(open(f))
    rs, ps, fs, es = [], [], [], []

    for pc in precision_criterions:
        fs.append(0)
        rs.append(0)
        ps.append(0)
        es.append(0)
        for r in results:
            if 'result' in r:
                r, p, score, e, _ = evaluation.evaluate_by_label(
                    r['label'], r['result'], pc)
            else:
                r, p, score, e, _ = evaluation.evaluate_by_label(
                    r['label'], r['results'][0][-1], pc)
            fs[-1] += score
            rs[-1] += r
            ps[-1] += p
            es[-1] += e
        rs[-1] /= len(results)
        ps[-1] /= len(results)
        es[-1] /= len(results)
        fs[-1] /= len(results)
    return rs, ps, fs, es


def plot_of_average():
    """
    对比实验图
    """
    # 误差容忍度范围
    X = range(0, 151, 10)
    MY1, MY2, MY3, MY4 = f1_scores(os.path.join(
        result_dir, 'prodrift-125-fwin.json'), X)
    Y1, Y2, Y3, Y4 = f1_scores(os.path.join(
        result_dir, '[最小长度实验]-[方法offline]-[半径10]-[fixed].json'.decode('utf-8')), X)
    print X
    print [round(i, 2) for i in MY3]
    print [round(i, 2) for i in Y3]
    print [round(i, 2) for i in MY4]
    print [round(i, 2) for i in Y4]

    # plt.subplot(221)
    # plt.plot(X, MY1, 'o-r', lw=2, label='Maaradji\'s Method')
    # plt.plot(X, Y1, 's-b', lw=2, label='Our Method')
    # plt.legend()
    # plt.ylabel('Recall', fontsize=12)
    # plt.xlabel('Error Tolerance', fontsize=12)
    # plt.title('Average of Recall', {'fontsize': 12})
    #
    # plt.subplot(222)
    # plt.plot(X, MY2, 'o-r', lw=2, label='Maaradji\'s Method')
    # plt.plot(X, Y2, 's-b', lw=2, label='Our Method')
    # plt.legend()
    # plt.ylabel('Precision', fontsize=12)
    # plt.xlabel('Error Tolerance', fontsize=12)
    # plt.title('Average of Precision', {'fontsize': 12})

    plt.subplot(121)
    plt.plot(X, MY3, 'o-', lw=2, color='blue', label='Maaradji\'s Method')
    plt.plot(X, Y3, 's-', lw=2, color='blue', label='Our Method')
    plt.legend()
    plt.ylabel('F-score')
    plt.xlabel('Error Tolerance')
    plt.title('(a) Mean F-socre')

    plt.subplot(122)
    plt.plot(X, MY4, 'o-', lw=2, color='blue', label='Maaradji\'s Method')
    plt.plot(X, Y4, 's-', lw=2, color='blue', label='Our Method')
    plt.legend()
    plt.ylabel('Detection Error')
    plt.xlabel('Error Tolerance')
    plt.title('(b) Mean Error')

    plt.subplots_adjust(top=0.92, bottom=0.15, left=0.08,
                        right=0.96, hspace=0.25, wspace=0.35)
    plt.show()


def plotOfCandidates():
    """
    候选变更点分布图
    """
    window_sizes = [30, 150, 750]
    item_seqs = ["(a)", "(b)", "(c)"]
    dd = DriftDetector()
    dd.set_log(
        r"./logs/[10 500]-[0, 531, 1061, 1532, 2001, 2538, 3002, 3551, 4010, 4523, 5009].mxml")
    dd.extract()
    N = len(dd.traces)
    xticks = range(0, 5001, 500)
    colors = ['red', 'blue', 'green']

    labels = [531, 1061, 1532, 2001, 2538, 3002, 3551, 4010, 4523]
    plt_pos = 130

    def draw_labels():
        for _, label in enumerate(labels):
            plt.plot([label, label], [0, max(Y) + 5],
                     '--', color="#888888", linewidth=0.5)

    fig, ax = plt.subplots(nrows=1, ncols=3, sharex=True, sharey=True)

    for i, window_size in enumerate(window_sizes):
        dd.partition(window_size)
        X, Y = dd.candidates()

        plt.subplot(plt_pos + i + 1)
        draw_labels()
        plt.plot(X, Y, 'o', color="blue", markersize=4)
        plt.xlim([0, 5100])
        plt.xticks(xticks, rotation=45)
        plt.ylim([0, max(Y) + 5])
        # plt.gca().annotate('Trace Index', xy=(0.9, -0.05), ha='left',
        #                    va='top', xycoords='axes fraction', fontsize=10)
        plt.title('%s MWS = %d' %
                  (item_seqs[i], window_size), fontsize=11)
    plt.subplots_adjust(top=0.90, bottom=0.20, left=0.06,
                        right=0.99, hspace=0.5, wspace=0.15)
    fig.text(0.5, 0.02, 'Trace Index', ha='center')
    fig.text(0.01, 0.5, 'Relation Index', va='center', rotation='vertical')
    plt.show()

def plot_of_candidate():
    window_sizes = [30, 150, 750]
    colors = ['#FFA475', '#A9FF8F', '#000080']
    marker = ['o', 'o', 'o']
    dd = DriftDetector()
    dd.set_log(r"./logs/[10 500]-[0, 531, 1061, 1532, 2001, 2538, 3002, 3551, 4010, 4523, 5009].mxml")
    dd.extract()
    for i, w in enumerate(window_sizes):
        dd.partition(w)
        X, Y = dd.candidates()
        plt.plot(X, Y, marker[i], color=colors[i], markersize=4)

    labels = [531, 1061, 1532, 2001, 2538, 3002, 3551, 4010, 4523]
    for x in labels:
        plt.plot([x, x], [0, max(Y) + 5], '--', color="#999999", linewidth=0.5)

    plt.xlim([0, 5200])
    plt.ylim([0, max(Y) + 5])
    plt.xticks(range(0, 5001, 500))
    plt.xlabel('Trace Index')
    plt.ylabel('Relation Index')
    plt.legend()
    plt.subplots_adjust(top=0.96, bottom=0.16, left=0.06, right=0.96, hspace=0.5, wspace=0.35)

    plt.show()

if __name__ == "__main__":
    plot_of_min_len()
    # plot_of_radius_4_in_1()
    # plot_of_candidate()
    # plot_of_radius()
    # plot_of_average()
    # plotOfCandidates()
