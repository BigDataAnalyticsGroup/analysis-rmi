#!python3
import matplotlib.pyplot as plt
import os
import pandas as pd
import warnings

# Ignore warnings
warnings.filterwarnings( "ignore")


def plot(x, y, xlabel, ylabel, filename):
    n_cols = len(configs)
    n_rows = len(datasets)

    fig, axs = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4.2*n_rows), sharey=True, sharex=True)
    fig.tight_layout()

    for row, dataset in enumerate(datasets):
        for col, config in enumerate(configs):
            ax = axs[row,col]
            for bound in bounds:
                data = df[(df['dataset']==dataset) & (df['config']==config) & (df['bounds']==bound)]
                ax.plot(data[x], data[y], label=bound, marker='o', alpha=0.7)

            # Axes labels
            ax.set_title(f'{dataset} ({config})')
            if row==n_rows - 1:
                ax.set_xlabel(xlabel)
            if col==0:
                ax.set_ylabel(ylabel)

            # Visuals
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.grid()
            ax.legend(ncol=1)

    fig.savefig(os.path.join(path, filename), bbox_inches='tight')


if __name__ == "__main__":
    path = 'results'

    # Read csv file
    file = os.path.join(path, 'rmi_intervals.csv')
    df = pd.read_csv(file, delimiter=',', header=0, comment='#')

    # Compute model combinations and metrics
    df['config'] = df['layer1'] + '$\mapsto$' + df['layer2']
    df['size_in_MiB'] = df['size_in_bytes'] / (1024 * 1024)

    datasets = sorted(df['dataset'].unique())
    configs = sorted(df['config'].unique())
    bounds = sorted(df['bounds'].unique())

    #  Plot mean interval size
    filename = 'rmi_intervals-mean_interval.pdf'
    print(f'Plotting mean interval to \'{filename}\'...')
    plot('size_in_MiB', 'mean_interval', 'Index size [MiB]', 'Mean error\ninterval size', filename)

    #  Plot median interval size
    filename = 'rmi_intervals-median_interval.pdf'
    print(f'Plotting median interval to \'{filename}\'...')
    plot('size_in_MiB', 'median_interval', 'Index size [MiB]', 'Median error\ninterval size', filename)

    #  Plot max interval size
    filename = 'rmi_intervals-max_interval.pdf'
    print(f'Plotting max interval to \'{filename}\'...')
    plot('size_in_MiB', 'max_interval', 'Index size [MiB]', 'Max error\ninterval size', filename)
