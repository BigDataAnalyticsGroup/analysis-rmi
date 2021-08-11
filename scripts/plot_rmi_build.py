#!python3
import matplotlib.pyplot as plt
import os
import pandas as pd
import warnings

# Ignore warnings
warnings.filterwarnings( "ignore")


def plot_layer1_types():
    n_cols = len(datasets)
    n_rows = 1

    bound = 'none'
    l2 = 'linear_spline'

    fig, axs = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4.2*n_rows), sharey=True, sharex=True)
    fig.tight_layout()

    for col, dataset in enumerate(datasets):
        ax = axs[col]
        for l1 in l1models:
            data = df[
                    (df['dataset']==dataset) &
                    (df['layer1']==l1) &
                    (df['layer2']==l2) &
                    (df['bounds']==bound)
            ]
            if not data.empty:
                ax.plot(data['size_in_MiB'], data['build_in_s'], marker='o', alpha=0.7, label=f'{l1}$\mapsto${l2}')

        # Axes labels
        ax.set_title(dataset)
        if col==0:
            ax.set_ylabel('Build time [s]')
        ax.set_xlabel('Index size [MiB]')

        # Visuals
        ax.set_ylim(bottom=0)
        ax.set_xscale('log')
        ax.grid()
        ax.legend(ncol=1)

    fig.savefig(os.path.join(path, 'rmi_build-layer1_types.pdf'), bbox_inches='tight')


def plot_layer2_types():
    n_cols = len(datasets)
    n_rows = 1

    bound = 'none'
    l1models = ['linear_spline', 'cubic_spline']

    fig, axs = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4.2*n_rows), sharey=True, sharex=True)
    fig.tight_layout()

    for col, dataset in enumerate(datasets):
        ax = axs[col]
        for l1 in l1models:
            for l2 in l2models:
                data = df[
                        (df['dataset']==dataset) &
                        (df['layer1']==l1) &
                        (df['layer2']==l2) &
                        (df['bounds']==bound)
                ]
                if not data.empty:
                    ax.plot(data['size_in_MiB'], data['build_in_s'], marker='o', alpha=0.7, label=f'{l1}$\mapsto${l2}')

        # Axes labels
        ax.set_title(dataset)
        if col==0:
            ax.set_ylabel('Build time [s]')
        ax.set_xlabel('Index size [MiB]')

        # Visuals
        ax.set_ylim(bottom=0)
        ax.set_xscale('log')
        ax.grid()
        ax.legend(ncol=1)

    fig.savefig(os.path.join(path, 'rmi_build-layer2_types.pdf'), bbox_inches='tight')


def plot_bounds():
    n_cols = len(datasets)
    n_rows = 1

    l1 = 'linear_spline'
    l2 = 'linear_regression'

    fig, axs = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4.2*n_rows), sharey=True, sharex=True)
    fig.tight_layout()

    for col, dataset in enumerate(datasets):
        ax = axs[col]
        for bound in bounds:
            data = df[
                    (df['dataset']==dataset) &
                    (df['layer1']==l1) &
                    (df['layer2']==l2) &
                    (df['bounds']==bound)
            ]
            if not data.empty:
                ax.plot(data['size_in_MiB'], data['build_in_s'], marker='o', alpha=0.7, label=bound)

        # Axes labels
        ax.set_title(f'{dataset} ({l1}$\mapsto${l2})')
        if col==0:
            ax.set_ylabel('Build time [s]')
        ax.set_xlabel('Index size [MiB]')

        # Visuals
        ax.set_ylim(bottom=0)
        ax.set_xscale('log')
        ax.grid()
        ax.legend(ncol=1)

    fig.savefig(os.path.join(path, 'rmi_build-bounds.pdf'), bbox_inches='tight')


if __name__ == "__main__":
    path = 'results'

    # Read csv file
    file = os.path.join(path, 'rmi_build.csv')
    df = pd.read_csv(file, delimiter=',', header=0, comment='#')

    # Compute median of lookup times
    df = df.groupby(['dataset','layer1','layer2','n_models','bounds']).median().reset_index()

    # Compute metrics
    df['size_in_MiB'] = df['size_in_bytes'] / (1024 * 1024)
    df['build_in_s'] = df['build_time'] / 1_000_000_000

    datasets = sorted(df['dataset'].unique())
    bounds = sorted(df['bounds'].unique())
    l1models = sorted(df['layer1'].unique())
    l2models = sorted(df['layer2'].unique())

    # Plot layer1 types
    plot_layer1_types()

    # Plot layer2 types
    plot_layer2_types()

    # Plot bounds
    plot_bounds()
