#!python3
import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np
import warnings

# Ignore warnings
warnings.filterwarnings( "ignore")


def plot(x, y, xlabel, ylabel, filename, ylim_bottom=None, ylim_top=None, with_binary=True):
    n_cols = len(datasets)
    n_rows = 1

    fig, axs = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4.2*n_rows), sharey=True, sharex=True)
    fig.tight_layout()

    for i, dataset in enumerate(datasets):
        ax = axs[i]
        for index in indexes:
            data = df[(df['dataset'] == dataset) & (df['index'] == index)]
            if index == 'Binary search':
                ax.axhline(y=data[y].iloc[0], label=index, color='.2', dashes=(2, 1)) if with_binary else True
            else:
                marker = markers.get(index, '*')
                ax.scatter(x=data[x], y=data[y], label=index, marker=marker, alpha=0.7)

        # Axes labels
        ax.set_title(dataset)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel) if i == 0 else True

        # Visuals
        ax.set_xscale('log')
        ax.grid()
        ax.legend(ncol=2)
        ax.set_ylim(bottom=ylim_bottom, top=ylim_top)

    fig.savefig(os.path.join(path, filename), bbox_inches='tight')


def plot_lookup_shares(filename):
    n_cols = len(datasets)
    n_rows = 1

    fig, axs = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4.2*n_rows), sharey=True, sharex=False)
    fig.tight_layout()

    for i, dataset in enumerate(datasets):
        ax = axs[i]

        # Gather data of fastest configuration per index
        labels = []
        evals = []
        searches = []

        for index in indexes:
            data = df[(df['dataset'] == dataset) & (df['index'] == index)].sort_values(['lookup_in_ns']).reset_index()
            if not data.empty:
                row = data.iloc[0] # fastest configuration
                labels.append(index)
                evals.append(row['eval_in_ns'])
                searches.append(row['search_in_ns'])

        # Plot results
        ax.bar(labels, evals, color='0.6', edgecolor='black', linewidth=1.5, label='Evaluation')
        ax.bar(labels, searches, color='0.9', edgecolor='black', linewidth=1.5, label='Search', bottom=evals)

        # labels
        ax.set_title(dataset)
        ax.set_xticklabels(labels=labels, rotation=90)
        ax.set_ylabel('Lookup time [ns]') if i == 0 else True

        # Visuals
        ax.grid()
        ax.legend(ncol=2,loc='upper center')

    fig.savefig(os.path.join(path, filename), bbox_inches='tight')


if __name__ == "__main__":
    path = 'results'

    # Read csv file
    file = os.path.join(path, 'index_comparison.csv')
    df = pd.read_csv(file, delimiter=',', header=0, comment='#')
    df = df.replace({np.nan: '-'})

    # Compute medians and metrics
    df = df.groupby(['dataset', 'index', 'config']).median().reset_index()
    df['size_in_MiB'] = df['size_in_bytes'] / (1024 * 1024)
    df['build_in_s'] = df['build_time'] / 1000000000
    df['eval_in_ns'] = df['eval_time'] / df['n_samples']
    df['lookup_in_ns'] = df['lookup_time'] / df['n_samples']
    df['search_in_ns'] = df['lookup_in_ns'] - df['eval_in_ns']

    datasets = sorted(df['dataset'].unique())
    indexes = sorted(df['index'].unique())

    markers = {
        'ALEX': '^',
        'ART': 'X',
        'B-tree': 'p',
        'Compact Hist-Tree': 'x',
        'PGM-index': 's',
        'RadixSpline': '+',
        'RMI': 'o',
    }

    # Plot lookup times against index size
    filename = 'index_comparison-lookup_time.pdf'
    print(f'Plotting lookup time results to \'{filename}\'...')
    plot('size_in_MiB', 'lookup_in_ns', 'Index size [MiB]', 'Lookup time [ns]',
            filename, ylim_bottom=0)

    # Plot build times against index size
    filename = 'index_comparison-build_time.pdf'
    print(f'Plotting build time results to \'{filename}\'...')
    build_times = sorted(df['build_in_s'])
    threshold= build_times[int(len(build_times)*0.97)] # Cut off slowest 3% in plot
    plot('size_in_MiB', 'build_in_s', 'Index size [MiB]', 'Build time [s]',
            filename, ylim_bottom=-1, ylim_top=threshold, with_binary=False)

    # Plot share of eval time and search time in overall lookup time
    filename = 'index_comparison-lookup_shares.pdf'
    print(f'Plotting lookup times shares to \'{filename}\'...')
    plot_lookup_shares(filename)

