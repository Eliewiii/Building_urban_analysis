import matplotlib.pyplot as plt
import numpy as np

# Sample data
data = [ [1, 2, 5, 6, 7,18],
         [2, 3, 4, 6, 8, 9, 10],
         [5, 6, 7, 8, 9, 10, 11],
         [6, 7, 8, 10, 12, 13, 14] ]


positions = [1, 1/4., 1/9.,1/16.]
base_width = 0.2

dpi=1000

fig, ax = plt.subplots(dpi=dpi)

# Iterate over data and positions to manually plot each box
for pos, d in zip(positions, data):
    # Compute quartiles and whiskers
    q1 = np.percentile(d, 25)
    q2 = np.median(d)
    q3 = np.percentile(d, 75)
    iqr = q3 - q1
    whisker_min = np.min([element for element in d if  element>= q1 - 1.5 * iqr])
    whisker_max = np.max( [element for element in d if  element<= q3 + 1.5 * iqr])

    outliers = [element for element in d if (element < whisker_min or element > whisker_max)]

    # Calculate width to ensure constant visual width on a logarithmic scale
    width_l = pos / (10 ** (base_width / 2))
    width_r = pos * (10 ** (base_width / 2))

    # Draw the box
    box = plt.Rectangle((width_l, q1), width_r - width_l, q3 - q1, edgecolor='black', facecolor='lightblue')
    ax.add_patch(box)

    # Draw the median line
    plt.plot([width_l*1.01, width_r*0.99], [q2, q2], color='black')  # 1% margin to avoid overlap with box

    # Draw the whiskers
    plt.plot([pos, pos], [whisker_min, q1*0.99], color='black')  # 1% margin to avoid overlap with box
    plt.plot([pos, pos], [q3*1.01, whisker_max], color='black')  # 1% margin to avoid overlap with box

    # Draw the whisker caps
    plt.plot([pos - (width_r - width_l) / 4, pos + (width_r - width_l) / 4], [whisker_min, whisker_min],
             color='black')
    plt.plot([pos - (width_r - width_l) / 4, pos + (width_r - width_l) / 4], [whisker_max, whisker_max],
             color='black')

    # Add outliers
    # plt.scatter([pos] * len(outliers), outliers, marker='o', color='red', s=30, zorder=3)
    # plt.scatter([pos] * len(outliers), outliers, marker='o', color='red', s=300, edgecolor='black', linewidth=1, zorder=3)
    plt.scatter([pos] * len(outliers), outliers, marker='o', color='white', s=50, edgecolor='black', linewidth=2, zorder=4)


# Set x-axis to logarithmic scale
ax.set_xscale('log')

# Customize the x-axis ticks and labels
# plt.xticks(positions, ['Category 1', 'Category 2', 'Category 3'])

# Add title and labels
# plt.title('Box Plot Example with Logarithmic X-axis')
plt.xlabel('Category')
plt.ylabel('Values')

# Show the plot
plt.show()