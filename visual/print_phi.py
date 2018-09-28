#!/usr/bin/python3
import matplotlib as mpl
mpl.use('Agg')

from matplotlib.ticker import FormatStrFormatter
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import math

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

# # Dashed line for sensors
# plt.plot(
#   [a for a in range(1, 256)],
#   [a for a in range(1, 256)],
#   '--',
#   color=grey_color
# )

ntox = {0:'X', 1:'Y', 2:'Z'}

def hit_phi(hit):
  if (hit.sensor_number % 2) == 0:
    phi = math.atan2(hit.y, hit.x)
    less_than_zero = phi < 0
    return phi + less_than_zero * 2 * math.pi
  return math.atan2(hit.y, hit.x)


def print_event_2d_phi(event, tracks=[], track_color=0, filename="event_phi"):  
  fig = plt.figure(figsize=(16*plotscale, 9*plotscale))
  ax = plt.axes()

  # Limits of the sensors
  limits = [(0, 2 * math.pi), (-math.pi, math.pi)]
  shift = 0.4
  # for s in event.sensors[::2]:
  #   plt.plot(
  #     [s.z+shift, s.z+shift],
  #     [limits[0][0], limits[0][1]],
  #     color=grey_color,
  #     alpha=0.4,
  #     linewidth=4
  #   )

  for s in event.sensors[1::2]:
    plt.plot(
      [s.z+shift, s.z+shift],
      [limits[1][0], limits[1][1]],
      color=grey_color,
      alpha=0.4,
      linewidth=4
    )

  # Print X versus Phi
  plt.scatter(
    [h[2] for h in event.hits if h.sensor_number % 2 == 1],
    [hit_phi(h) for h in event.hits if h.sensor_number % 2 == 1],
    color=default_color,
    s=2*scale
  )

  # for t in [t for t in tracks if len(t.hits)==3]:
  #   plt.plot(
  #     [h[2] for h in t.hits],
  #     [hit_phi(h) for h in t.hits],
  #     color=colors[track_color],
  #     linewidth=1
  #   )

  plt.tick_params(axis='both', which='major', labelsize=4*scale)
  plt.xlabel("Z", fontdict={'fontsize': 4*scale})
  plt.ylabel("φ", fontdict={'fontsize': 4*scale}, rotation='horizontal')

  plt.savefig(filename + ".png", bbox_inches='tight', pad_inches=0.2)
  plt.savefig(filename + ".pdf", transparent=True, bbox_inches='tight', pad_inches=0.2)

  plt.close()
