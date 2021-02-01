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
plotscale = 1.5

# # Dashed line for modules
# plt.plot(
#   [a for a in range(1, 256)],
#   [a for a in range(1, 256)],
#   '--',
#   color=grey_color
# )

ntox = {0:'X', 1:'Y', 2:'Z'}

def print_event_2d(event, tracks=[], x=2, y=0, track_color=0, filename="visual.png", save_to_file=False, modules=[]):
  """
  A function to print events. It produces a 2D plot
  and either prints or saves it to a file.

  Arguments
  ---------
  
  event : the event to be printed
  modules : list of modules to be printed
  tracks : tracks to print
  track_color : color of tracks (in 0-20 range)
  x : index to be used as x axis
  y : index to be used as y axis
  save_to_file : switches between saving output to file or showing it (default)
  filename : file where to save visualization
  """
  limits = ((24, -74), (-24, 74))
  shift = 0.5

  if modules:
    fig = plt.figure()
    ax = plt.axes()

    for i in modules:
      m = event.modules[i]
      limit = limits[i % 2]
      rect = mpatches.Rectangle((min(m.z)-shift,limit[0]),max(m.z)-min(m.z)+2*shift,limit[1],edgecolor=grey_color,facecolor=grey_color,alpha=0.4)
      ax.add_patch(rect)
    plt.scatter(
      [h[x] for h in event.hits if h.module_number in modules],
      [h[y] for h in event.hits if h.module_number in modules],
      color=default_color,
      s=2*scale
    )

  else:
    fig = plt.figure(figsize=(16*plotscale, 9*plotscale))
    ax = plt.axes()

    for i, m in enumerate(event.modules):
      limit = limits[i % 2]
      rect = mpatches.Rectangle((min(m.z)-shift,limit[0]),max(m.z)-min(m.z)+2*shift,limit[1],edgecolor=grey_color,facecolor=grey_color,alpha=0.4)
      ax.add_patch(rect)

    plt.scatter(
      [h[x] for h in event.hits],
      [h[y] for h in event.hits],
      color=default_color,
      s=2*scale
    )

  for t in tracks:
    plt.plot(
      [h[x] for h in t.hits],
      [h[y] for h in t.hits],
      color=colors[track_color],
      linewidth=1
    )

  plt.tick_params(axis='both', which='major', labelsize=4*scale)
  plt.xlabel(ntox[x], fontdict={'fontsize': 4*scale})
  plt.ylabel(ntox[y], fontdict={'fontsize': 4*scale}, rotation='horizontal')

  if save_to_file:
    plt.savefig(filename, bbox_inches='tight', pad_inches=0.2)
    plt.close()
  else:
    plt.show()
