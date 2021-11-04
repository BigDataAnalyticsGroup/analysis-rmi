#!python3
import matplotlib.pyplot as plt
import os
import pandas as pd
import warnings

# Ignore warnings
warnings.filterwarnings( "ignore")


def plot(x, y, xlabel, ylabel, filename):
    n_cols = len(datasets)
    n_rows = 1

    fig, axs = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4.2*n_rows), sharey=True, sharex=True)
    fig.tight_layout()

    for i, dataset in enumerate(datasets):
        ax = axs[i]
        for l1 in l1_models:
            for l2 in l2_models:
                data = df[(df['dataset']==dataset) & (df['layer1']==l1) & (df['layer2']==l2)]
                ax.plot(data[x], data[y], label=f'{l1}$\mapsto${l2}', marker='.', alpha=0.7)

        # Axes labels
        ax.set_title(dataset)
        ax.set_xlabel(xlabel)
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
    file = os.path.join(path, 'rmi_errors.csv')
    df = pd.read_csv(file, delimiter=',', header=0, comment='#')

    datasets = sorted(df['dataset'].unique())
    l1_models = sorted(df['layer1'].unique())
    l2_models = sorted(df['layer2'].unique())

    # Plot mean absolute error
    filename = 'rmi_errors-mean_absolute_error.pdf'
    print(f'Plotting mean absolute error to \'{filename}\'...')
    plot('n_models', 'mean_ae', '# of segments', 'Mean absolute error', filename)

    # Plot mean absolute error
    filename = 'rmi_errors-median_absolute_error.pdf'
    print(f'Plotting median absolute error to \'{filename}\'...')
    plot('n_models', 'median_ae', '# of segments', 'Median absolute error', filename)

    # Plot max absolute error
    filename = 'rmi_errors-max_absolute_error.pdf'
    print(f'Plotting max absolute error to \'{filename}\'...')
    plot('n_models', 'max_ae', '# of segments', 'Maximum absolute error', filename)
