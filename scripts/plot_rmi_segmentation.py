#!python3
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import os
import pandas as pd
import warnings

# Ignore warnings
warnings.filterwarnings( "ignore")


def plot_frac_empty(filename='rmi_segmentation-frac_empty.pdf'):
    n_cols = len(datasets)
    n_rows = 1

    fig, axs = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4.2*n_rows), sharey=True, sharex=True)
    fig.tight_layout()

    for col, dataset in enumerate(datasets):
        ax = axs[col]
        for model in models:
            data = df[
                    (df['dataset']==dataset) &
                    (df['model']==model)
            ]
            if not data.empty:
                ax.plot(data['n_segments'], data['frac_empty'], marker='o', alpha=0.7, label=model)

        # Axes labels
        ax.set_title(dataset)
        if col==0:
            ax.set_ylabel('percentage of empty segments')
        ax.set_xlabel('# of segments')

        # Visuals
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
        ax.set_xscale('log', base=2)
        ax.grid()
        ax.legend(ncol=1)

    fig.savefig(os.path.join(path, filename), bbox_inches='tight')


def plot_max_segment(filename='rmi_segmentation-max_segment.pdf'):
    n_cols = len(datasets)
    n_rows = 1

    fig, axs = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4.2*n_rows), sharey=True, sharex=True)
    fig.tight_layout()

    for col, dataset in enumerate(datasets):
        ax = axs[col]
        for model in models:
            data = df[
                    (df['dataset']==dataset) &
                    (df['model']==model)
            ]
            if not data.empty:
                ax.plot(data['n_segments'], data['max'], marker='o', alpha=0.7, label=model)

        # Axes labels
        ax.set_title(dataset)
        if col==0:
            ax.set_ylabel('size of largest segment')
        ax.set_xlabel('# of segments')

        # Visuals
        ax.set_yscale('log')
        ax.set_xscale('log', base=2)
        ax.grid()
        ax.legend(ncol=1)

    fig.savefig(os.path.join(path, filename), bbox_inches='tight')

if __name__ == "__main__":
    path = 'results'

    # Read csv file
    file = os.path.join(path, 'rmi_segmentation.csv')
    df = pd.read_csv(file, delimiter=',', header=0, comment='#')

    # Compute metrics
    df['frac_empty'] = df['n_empty'] / df['n_segments']

    datasets = sorted(df['dataset'].unique())
    models = sorted(df['model'].unique())
    n_segments = sorted(df['n_segments'].unique())

    # Plot empty segments
    filename = 'rmi_segmentation-frac_empty.pdf'
    print(f'Plotting empty segments to \'{filename}\'...')
    plot_frac_empty(filename)

    # Plot max segment
    filename = 'rmi_segmentation-max_segment.pdf'
    print(f'Plotting max segments to \'{filename}\'...')
    plot_max_segment(filename)


