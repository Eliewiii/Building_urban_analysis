"""
Functions to plot box charts.
"""

import matplotlib.pyplot as plt
import numpy as np


def plot_xlog_box_chart(data: list, x_positions: list, x_label: str, y_label: str, fig_height: float = 6.,
                        fig_width: float = 9., base_width: float = 0.1, title: str = None,
                        box_color='lightblue', outlier_color='black', dpi=1000):
    """
    Plot a box chart with x-axis on a logarithmic scale.
    param data: List of lists. Each list contains the data for one box.
    param x_positions: List of floats. The x-positions of the boxes.
    param base_width: Float. The width of the boxes.
    param box_color: String. The color of the boxes.
    param outlier_color: String. The color of the outliers.
    param dpi: Int. The resolution of the plot.
    """
    # Calculate figsize based on length and width, and convert to inches
    figsize = (fig_width, fig_height)
    # Create a box plot manually to control the widths
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    # Iterate over data and positions to manually plot each box
    for pos, d in zip(x_positions, data):
        # Compute quartiles and whiskers
        q1 = np.percentile(d, 25)
        q2 = np.median(d)
        q3 = np.percentile(d, 75)
        iqr = q3 - q1
        whisker_min = np.min([element for element in d if element >= q1 - 1.5 * iqr])
        whisker_max = np.max([element for element in d if element <= q3 + 1.5 * iqr])

        outliers = [element for element in d if (element < whisker_min or element > whisker_max)]

        # Calculate width to ensure constant visual width on a logarithmic scale
        width_l = pos / (10 ** (base_width / 2))
        width_r = pos * (10 ** (base_width / 2))

        # Draw the box
        box = plt.Rectangle((width_l, q1), width_r - width_l, q3 - q1, edgecolor=outlier_color,
                            facecolor=box_color)
        ax.add_patch(box)

        # Draw the median line
        plt.plot([width_l * 1.01, width_r * 0.99], [q2, q2],
                 color=outlier_color)  # 1% margin to avoid overlap with box

        # Draw the whiskers
        plt.plot([pos, pos], [whisker_min, q1 * 0.99],
                 color=outlier_color)  # 1% margin to avoid overlap with box
        plt.plot([pos, pos], [q3 * 1.01, whisker_max],
                 color=outlier_color)  # 1% margin to avoid overlap with box

        # Draw the whisker caps
        plt.plot([pos - (width_r - width_l) / 4, pos + (width_r - width_l) / 4], [whisker_min, whisker_min],
                 color=outlier_color)
        plt.plot([pos - (width_r - width_l) / 4, pos + (width_r - width_l) / 4], [whisker_max, whisker_max],
                 color=outlier_color)

        # Add outliers
        plt.scatter([pos] * len(outliers), outliers, marker='o', color='white', s=30, edgecolor='black',
                    linewidth=2, zorder=4)

    # Set x-axis to logarithmic scale
    ax.set_xscale('log')

    # Add title and labels

    plt.subplots_adjust(top=0.95, bottom=0.1, left=0.1, right=0.95, hspace=0.2, wspace=0.2)
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    # Save the figure in the Figures folder
    plt.savefig(f'Figures/{title}.png', dpi=dpi)


if __name__ == "__main__":
    # Create some data
    data = [[1, 2, 5, 6, 7, 18],
            [2, 3, 4, 6, 8, 9, 10],
            [5, 6, 7, 8, 9, 10, 11],
            [6, 7, 8, 10, 12, 13, 14]]

    positions = [1, 1 / 4., 1 / 9., 1 / 16.]
    base_width = 0.2

    dpi = 1000

    plot_xlog_box_chart(data=data, x_positions=positions, x_label='Category', y_label='Values')
