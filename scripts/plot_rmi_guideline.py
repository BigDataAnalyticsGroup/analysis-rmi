#!python3
import matplotlib.pyplot as plt
import os
import pandas as pd
import itertools
import warnings

# Ignore warnings
warnings.filterwarnings( "ignore")


def plot_guideline(filename='rmi_guideline.pdf'):
    n_cols = len(datasets)
    n_rows = 1

    fig, axs = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4.2*n_rows), sharey=True, sharex=True)
    fig.tight_layout()

    for col, dataset in enumerate(datasets):
        ax = axs[col]
        fast_lookups = list()
        fast_sizes = list()
        guide_lookups = list()
        guide_sizes = list()
        for budget in budgets:

            # Fastest configuration
            fast_confs = df[
                (df['dataset']==dataset) &
                (df['budget_in_bytes']==budget) &
                (df['is_guideline']==False)
            ]
            fast_lookup = fast_confs['lookup_in_ns'].min()
            fast_conf = fast_confs[fast_confs['lookup_in_ns']==fast_lookup]
            fast_size = fast_conf['size_in_bytes'].iloc[0]

            fast_lookups.append(fast_lookup)
            fast_sizes.append(fast_size)

            # Guideline configuration
            guide_conf = df[
                (df['dataset']==dataset) &
                (df['budget_in_bytes']==budget) &
                (df['is_guideline']==True)
            ]
            guide_lookup = guide_conf['lookup_in_ns'].iloc[0]
            guide_size = guide_conf['size_in_bytes'].iloc[0]

            guide_lookups.append(guide_lookup)
            guide_sizes.append(guide_size)

        # Plot lookup times
        ax.plot(fast_sizes, fast_lookups, marker='x', alpha=0.7, label='RMI (fastest)')
        ax.plot(guide_sizes, guide_lookups, marker='o', alpha=0.7, label='RMI (guideline)')

        # Axes labels
        ax.set_title(f'{dataset}')
        if col==0:
            ax.set_ylabel('Lookup time [ns]')
        ax.set_xlabel('Index size [MiB]')

        # Visuals
        if col==n_cols-1:
            ax.set_ylim(bottom=0)
        ax.set_xscale('log')
        ax.grid()
        ax.legend(ncol=1)

    fig.savefig(os.path.join(path, filename), bbox_inches='tight')


if __name__ == "__main__":
    path = 'results'

    # Read csv file
    file = os.path.join(path, 'rmi_guideline.csv')
    df = pd.read_csv(file, delimiter=',', header=0, comment='#')

    # Compute median of lookup times
    df = df.groupby(['dataset','layer1','layer2','n_models','bounds','search','is_guideline']).median().reset_index()

    # Compute metrics
    df['size_in_MiB'] = df['size_in_bytes'] / (1024 * 1024)
    df['lookup_in_ns'] = df['lookup_time'] / df['n_samples']

    datasets = sorted(df['dataset'].unique())
    budgets = sorted(df['budget_in_bytes'].unique())

    # Plot guideline
    filename = 'rmi_guideline.pdf'
    print(f'Plotting guideline to \'{filename}\'...')
    plot_guideline(filename)
