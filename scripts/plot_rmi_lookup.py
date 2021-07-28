#!python3
import matplotlib.pyplot as plt
import os
import pandas as pd
import warnings

# Ignore warnings
warnings.filterwarnings( "ignore")


def plot_model_types():
    n_cols = len(datasets)
    n_rows = 1

    bound = 'labs'
    search = 'binary'

    fig, axs = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4.2*n_rows), sharey=False, sharex=True)
    fig.tight_layout()

    for col, dataset in enumerate(datasets):
        ax = axs[col]
        for l1 in l1models:
            for l2 in l2models:
                data = df[
                        (df['dataset']==dataset) &
                        (df['layer1']==l1) &
                        (df['layer2']==l2) &
                        (df['bounds']==bound) &
                        (df['search']==search)
                ]
                if not data.empty:
                    ax.plot(data['size_in_MiB'], data['lookup_in_ns'], marker='o', alpha=0.7, label=f'{l1}$\mapsto${l2}')

        # Axes labels
        ax.set_title(dataset)
        if col==0:
            ax.set_ylabel('Lookup time [ns]')
        ax.set_xlabel('Index size [MiB]')

        # Visuals
        ax.set_ylim(bottom=0)
        ax.set_xscale('log')
        ax.grid()
        ax.legend(ncol=1)

    fig.savefig(os.path.join(path, 'rmi_lookup-model_types.pdf'), bbox_inches='tight')


def plot_bounds():
    configs = [('linear_spline','linear_regression'), ('cubic_spline', 'linear_spline')]

    n_cols = len(datasets)
    n_rows = len(configs)

    search = 'binary'

    fig, axs = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4.2*n_rows), sharey=False, sharex=True)
    fig.tight_layout()

    for col, dataset in enumerate(datasets):
        fastest = df[df['dataset']==dataset].sort_values('lookup_in_ns').iloc[0]['lookup_in_ns']
        for row, (l1, l2) in enumerate(configs):
            ax = axs[row,col]
            for bound in bounds:
                data = df[
                        (df['dataset']==dataset) &
                        (df['layer1']==l1) &
                        (df['layer2']==l2) &
                        (df['bounds']==bound) &
                        (df['search']==search) &
                        (df['lookup_in_ns'] < 8*fastest) # filter slow configurations
                ]
                if not data.empty:
                    ax.plot(data['size_in_MiB'], data['lookup_in_ns'], marker='o', alpha=0.7, label=f'{bound} ({search})')

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

    fig.savefig(os.path.join(path, 'rmi_lookup-bounds.pdf'), bbox_inches='tight')


def plot_searches():
    configs = [('linear_spline','linear_regression'), ('cubic_spline', 'linear_spline')]

    n_cols = len(datasets)
    n_rows = len(configs)

    search_configs = [('lind','binary'),('lind','model_biased_binary'),('none','model_biased_exponential'),('none',
    'model_biased_linear')]

    fig, axs = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4.2*n_rows), sharey=False, sharex=True)
    fig.tight_layout()

    for col, dataset in enumerate(datasets):
        fastest = df[df['dataset']==dataset].sort_values('lookup_in_ns').iloc[0]['lookup_in_ns']
        for row, (l1, l2) in enumerate(configs):
            ax = axs[row,col]
            for (bound,search) in search_configs:
                data = df[
                        (df['dataset']==dataset) &
                        (df['layer1']==l1) &
                        (df['layer2']==l2) &
                        (df['bounds']==bound) &
                        (df['search']==search) &
                        (df['lookup_in_ns'] < 8*fastest) # filter slow configurations
                ]
                if not data.empty:
                    ax.plot(data['size_in_MiB'], data['lookup_in_ns'], marker='o', alpha=0.7, label=f'{search} ({bound})')

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

    fig.savefig(os.path.join(path, 'rmi_lookup-searches.pdf'), bbox_inches='tight')


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
    plot_model_types()

    # Plot bounds
    plot_bounds()

    # Plot searches
    plot_searches()
