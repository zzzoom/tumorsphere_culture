import os
import numpy as np
import matplotlib.pyplot as plt

# Set the path to the directory containing the data files
data_dir = "/home/nate/Devel/tumorsphere_culture/data/sim_2_evolution_many_ps/averages/"

# Set the value of p for which to plot the data
p = 0.5

# Find the data file for the specified value of p
data_file = None
for file_name in os.listdir(data_dir):
    if file_name.startswith("average-sp-{}".format(
            p
        )):
        data_file = os.path.join(data_dir, file_name)
        break

# Read the data from the file
data = np.loadtxt(data_file, delimiter=",", skiprows=1)

# Extract the columns of interest
time = data[:, 0]
total_cells = data[:, 1]
active_cells = data[:, 2]
total_stem_cells = data[:, 3]
active_stem_cells = data[:, 4]

# Plot the curves
fig, ax = plt.subplots()
ax.plot(time, total_cells, label="Total Cells")
ax.plot(time, active_cells, label="Active Cells")
ax.plot(time, total_stem_cells, label="Total Stem Cells")
ax.plot(time, active_stem_cells, label="Active Stem Cells")

# Set y-axis scale to logarithmic
plt.yscale("log")

ax.set_xlabel("Time")
ax.set_ylabel("Cell Count")
ax.set_title("Evolution of Tumor Cell Populations")
ax.legend()

# to see the figure
# plt.show()

# Save the plot as a PNG file
plt.savefig(
    "/home/nate/Devel/tumorsphere_culture/data/sim_2_evolution_many_ps/averages_plots/average-sp-{}-log.png".format(
            p
        ),
    dpi=300,
)
# the dpi (dots per inch) is set to 100 by default, but it's too low for me
