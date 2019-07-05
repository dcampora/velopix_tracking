#!/usr/bin/python3
import matplotlib as mpl
mpl.use('Agg')

from matplotlib.ticker import FormatStrFormatter
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

# Beautiful colors
default_color = "#478DCB"
grey_color = "#D0D0D0"
colors = ["#CF3D1E", "#F15623", "#F68B1F", "#FFC60B", "#DFCE21",
  "#BCD631", "#95C93D", "#48B85C", "#00833D", "#00B48D", 
  "#60C4B1", "#27C4F4", "#3E67B1", "#4251A3", "#59449B", 
  "#6E3F7C", "#6A246D", "#8A4873", "#EB0080", "#EF58A0", "#C05A89"]

# Some default parameters for the figure
scale = 4
plotscale = 0.8

# # Dashed line for modules
# plt.plot(
#   [a for a in range(1, 256)],
#   [a for a in range(1, 256)],
#   '--',
#   color=grey_color
# )

ntox = {0:'X', 1:'Y', 2:'Z'}

def print_event_2d(ev, tracks=[], x=2, y=0, track_color=0, filename="visual.png"):  
  fig = plt.figure(figsize=(8*plotscale, 8*plotscale))
  ax = plt.axes()

  min_module = 10 * 2
  max_module = 15 * 2

  # Limits of the modules
  limits = [(-20, 50), (-50, 20)]
  shift = 1.0
  for s in ev.modules[::2]:
    if s.module_number > min_module and s.module_number <= max_module:
      plt.plot(
        [s.z+shift, s.z+shift],
        [limits[0][0], limits[0][1]],
        color=grey_color,
        alpha=0.4,
        linewidth=12)

  """
  for s in ev.modules[1::2]:
    plt.plot(
      [s.z+shift, s.z+shift],
      [limits[1][0], limits[1][1]],
      color=grey_color,
      alpha=0.4,
      linewidth=4
    )
  """

  plt.scatter(
    [h[x] for h in ev.hits if (h.module_number % 2) == 0 and (h.module_number > min_module) and (h.module_number <= max_module)],
    [h[y] for h in ev.hits if (h.module_number % 2) == 0 and (h.module_number > min_module) and (h.module_number <= max_module)],
    color=default_color,
    s=6*scale
  )

  # for t in tracks:
  #   number_of_hits_other_side = 0
  #   number_of_hits = 0
  #   for h in t.hits:
  #     if (h.module_number % 2) == 1:
  #       number_of_hits_other_side += 1
  #     elif h.module_number > min_module and h.module_number <= max_module:
  #       number_of_hits += 1

  #   if number_of_hits_other_side < 3 and number_of_hits >= 3:
  #     plt.plot(
  #       [h[x] for h in t.hits if (h.module_number % 2) == 0 and (h.module_number > min_module) and (h.module_number <= max_module)],
  #       [h[y] for h in t.hits if (h.module_number % 2) == 0 and (h.module_number > min_module) and (h.module_number <= max_module)],
  #       color="#000000",
  #       linewidth=1)

  # plt.tick_params(axis='both', which='major', labelsize=4*scale)
  # plt.xlabel(ntox[x], fontdict={'fontsize': 4*scale})
  # plt.ylabel(ntox[y], fontdict={'fontsize': 4*scale}, rotation='horizontal')
  # plt.axis('off')

  plt.tick_params(
    axis='x',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    bottom=False,      # ticks along the bottom edge are off
    top=False,         # ticks along the top edge are off
    labelbottom=False) # labels along the bottom edge are off

  plt.tick_params(
    axis='y',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    left=False,      # ticks along the bottom edge are off
    right=False,         # ticks along the top edge are off
    labelleft=False) # labels along the bottom edge are off

  plt.savefig(filename, bbox_inches='tight', pad_inches=0.2)
  plt.savefig(filename + ".pdf", bbox_inches='tight', pad_inches=0.2, transparent=True)
  plt.close()
