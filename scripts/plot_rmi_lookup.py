#!python3
import matplotlib.pyplot as plt
import os
import pandas as pd
import itertools
import warnings

# Ignore warnings
warnings.filterwarnings( "ignore")


def plot(filename='rmi_lookup.pdf'):
    n_rows = len(datasets)
    n_cols = len(l1models) * len(l2models)

    configs = itertools.product(l1models, l2models)

    fig, axs = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4.2*n_rows), sharey=True, sharex=True)
    fig.tight_layout()

    for col, (l1, l2) in enumerate(configs):
        for row, dataset in enumerate(datasets):
            ax = axs[row, col]
            for bound in bounds:
                for search in searches:
                    data = df[
                            (df['dataset']==dataset) &
                            (df['layer1']==l1) &
                            (df['layer2']==l2) &
                            (df['bounds']==bound) &
                            (df['search']==search)
                    ]
                    if not data.empty:
                        ax.plot(data['size_in_MiB'], data['lookup_in_ns'], marker='.', alpha=0.7, label=f'{bound}+{search}')

            # Axes labels
            ax.set_title(f'{dataset} ({l1}$\mapsto${l2})')
            if col==0:
                ax.set_ylabel('Lookup time [ns]')
            if row==n_rows-1:
                ax.set_xlabel('Index size [MiB]')

            # Visuals
            ax.set_ylim(bottom=0)
            ax.set_xscale('log')
            ax.grid()
            ax.legend(ncol=1)

    fig.savefig(os.path.join(path, filename), bbox_inches='tight')


if __name__ == "__main__":
    path = 'results'

    # Read csv file
    file = os.path.join(path, 'rmi_lookup.csv')
    df = pd.read_csv(file, delimiter=',', header=0, comment='#')

    # Compute median of lookup times
    df = df.groupby(['dataset','layer1','layer2','n_models','bounds','search']).median().reset_index()

    # Compute metrics
    df['size_in_MiB'] = df['size_in_bytes'] / (1024 * 1024)
    df['lookup_in_ns'] = df['lookup_time'] / df['n_samples']

    datasets = sorted(df['dataset'].unique())
    bounds = sorted(df['bounds'].unique())
    searches = sorted(df['search'].unique())
    l1models = sorted(df['layer1'].unique())
    l2models = sorted(df['layer2'].unique())

    # Plot model types
    filename = 'rmi_lookup.pdf'
    print(f'Plotting lookup time to \'{filename}\'...')
    plot(filename)
