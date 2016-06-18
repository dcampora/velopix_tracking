import event_model as em
import matplotlib.pyplot as plt
import json
import math

def open_file(number):
  f = open("velojson/" + str(number) + ".json")
  json_data = json.loads(f.read())
  event = em.event(json_data)
  f.close()
  return json_data, event

def are_compatible(hit_0, hit_1, max_slopes=(0.7, 0.7)):
  hit_distance = abs(hit_1[2] - hit_0[2])
  dxmax = max_slopes[0] * hit_distance
  dymax = max_slopes[1] * hit_distance
  return abs(hit_1[0] - hit_0[0]) < dxmax and \
         abs(hit_1[1] - hit_0[1]) < dymax

def distance(point_0, point_1):
  return math.sqrt(abs(point_0[0] - point_1[0]) + abs(point_0[1] - point_1[1]))

def get_longest_distance(ps):
  p1_max = None
  p2_max = None
  d_max = 0
  for p1 in ps:
    for p2 in ps:
      if p1 != p2 and p1[0] < p2[0]:
        dist = distance(p1, p2)
        if dist > d_max:
          d_max = dist
          p1_max = p1
          p2_max = p2
  return (p1_max, p2_max)

def simple_extrapolation(hit_0, hit_1, extrapolation_z):
  tx = (hit_1.x - hit_0.x) / (hit_1.z - hit_0.z)
  ty = (hit_1.y - hit_0.y) / (hit_1.z - hit_0.z)
  x  = hit_0.x + tx * (extrapolation_z - hit_0.z)
  y  = hit_0.y + ty * (extrapolation_z - hit_0.z)
  return x, y

# Beautiful colors
default_color = "#478DCB"
grey_color = "#D0D0D0"
colors = ["#CF3D1E", "#F15623", "#F68B1F", "#FFC60B", "#DFCE21",
  "#BCD631", "#95C93D", "#48B85C", "#00833D", "#00B48D", 
  "#60C4B1", "#27C4F4", "#3E67B1", "#4251A3", "#59449B", 
  "#6E3F7C", "#6A246D", "#8A4873", "#EB0080", "#EF58A0", "#C05A89"]
color_id = 0

# Some constants or default values
extrapolation_z = 1000
limits_xy = (800, 800)
maximum_hits_in_track = 25
foldername = "/home/dcampora/projects/tracking_wheels/graphs/"
filename = "default.png"
max_slope = (0.7, 0.7)
number_of_events = 1

# Some default values for the figure
fig = plt.figure(figsize=(16, 9))
ax = plt.axes()
plt.title("", fontdict={'fontsize': 20, 'family': 'source code pro'})
plt.xlabel("", fontdict={'family': 'source code pro'})
plt.ylabel("", fontdict={'family': 'source code pro'})

# f = open("velojson/0.json")
# json_data = json.loads(f.read())
# event = em.event(json_data)
# f.close()
# hit_dictionary = {h.id:h for h in event.hits}


## Scatter plot for all hits
# extrapolated_hits = {"x": [], "y": [], "color": [], "id": []}
# # Get all pairs of consecutive hits in consecutive sensors
# for s0, s1 in zip(reversed(event.sensors[:event.number_of_sensors-2]), reversed(event.sensors[2:])):
#   for h0 in s0:
#     for h1 in s1:
#       if are_compatible(h0, h1):
#         # Extrapolate hits to extrapolation_z
#         # Add to extrapolated_hits, in tuple {x, y} form
#         x, y = simple_extrapolation(h0, h1, extrapolation_z)
#         if abs(x) < limits_xy[0] and abs(y) < limits_xy[1]:
#           extrapolated_hits["x"].append(x)
#           extrapolated_hits["y"].append(y)
#           extrapolated_hits["color"].append(default_color)
#           if h0.id < h1.id:
#             extrapolated_hits["id"].append(str(h0.id) + str(h1.id))
#           else:
#             extrapolated_hits["id"].append(str(h1.id) + str(h0.id))
# plt.scatter(extrapolated_hits["x"], extrapolated_hits["y"], color=extrapolated_hits["color"], s=10.0)

# ## Scatter plot for MC hits
# mc_tracks_hits = {"x": [], "y": [], "color": [], "weight": []}
# hit_was_added = False
# mc_desc = {event.montecarlo['description'][i]:i for i in range(len(event.montecarlo['description']))}
# for p in event.montecarlo['particles']:
#   hits = p[mc_desc['mcp_hits']]
#   if hit_was_added:
#     color_id = (color_id + 1) % len(colors)
#     hit_was_added = False
#   for n in range(len(hits)-1):
#     h0_id, h1_id = hits[n], hits[n+1]
#     h0, h1 = hit_dictionary[h0_id], hit_dictionary[h1_id]
#     x, y = simple_extrapolation(h0, h1, extrapolation_z)
#     hit_was_added = True
#     mc_tracks_hits["x"].append(x)
#     mc_tracks_hits["y"].append(y)
#     mc_tracks_hits["color"].append(colors[color_id])
#     mc_tracks_hits["weight"].append(len(hits) * 10)
# plt.scatter(mc_tracks_hits["x"], mc_tracks_hits["y"], color=mc_tracks_hits["color"], s=mc_tracks_hits["weight"])

## Histogram of hits in a track's distances to others
# number_of_events = 1
# distances = []
# distances_to_other = []
# total_mc_segments = [0 for _ in range(maximum_hits_in_track)]
# found_mc_segments = [0 for _ in range(maximum_hits_in_track)]
# for i in range(number_of_events):
#   # Get an event
#   hit_dictionary = {h.id:h for h in event.hits}

#   # # Populate extrapolated_hits
#   # Get all pairs of consecutive hits in consecutive sensors
#   extrapolated_segments = []
#   for s0, s1 in zip(event.sensors[:event.number_of_sensors-2], event.sensors[2:]):
#     for h0 in s0:
#       for h1 in s1:
#         # if are_compatible(h0, h1, max_slope):
#         x, y = simple_extrapolation(h0, h1, extrapolation_z)
#         if abs(x) < limits_xy[0] and abs(y) < limits_xy[1]:
#           extrapolated_segments.append(em.segment(x, y, [h0, h1], color=default_color))

#   ## Plot with average distances to hits in the same track
#   # List of track segments
#   mc_extrapolated_segments = []
#   mc_tracks = []
#   mc_desc = {event.montecarlo['description'][i]:i for i in range(len(event.montecarlo['description']))}
#   for p in event.montecarlo['particles']:
#     hits = p[mc_desc['mcp_hits']]
#     mc_tracks.append([hit_dictionary[h] for h in hits])

#   for mc_track in mc_tracks:
#     mc_track_segments = []
#     for n in range(len(mc_track)-1):
#       h0, h1 = mc_track[n], mc_track[n+1]
#       if h0.sensor_number != h1.sensor_number:
#         x, y = simple_extrapolation(h0, h1, extrapolation_z)
#         mc_track_segments.append(em.segment(x, y, [h0, h1]))
#     mc_extrapolated_segments.append(mc_track_segments)

#     # Percentage of real track segments in extrapolated_segments
#     total_mc_segments[len(mc_track_segments)] += len(mc_track_segments)
#     for mc_segment in mc_track_segments:
#       if mc_segment in extrapolated_segments:
#         found_mc_segments[len(mc_track_segments)] += 1

#   existing_segments = []
#   for i in range(maximum_hits_in_track):
#     if total_mc_segments[i] == 0:
#       existing_segments.append(1)
#     else:
#       existing_segments.append(found_mc_segments[i] / total_mc_segments[i])
  
  # three_hit_mc_segments.append(found_mc_segments[3] / total_mc_segments[3])


  # Scatterplot the existing_segments
  # plt.scatter([i for i in range(maximum_hits_in_track)], existing_segments, color=default_color)

## All reconstructible segments with no slope limit (100 events)
plot_title = "All reconstructible segments with condition\ns0 == s1 - 2 or s0 == s1 - 1"
plt.xlabel("Track size")
plt.ylabel("Percentage of segments")

def classical_condition(hit_0, hit_1, max_slope=(0.7, 0.7)):
  # Sensors must be separted by two, there is a max slope
  return hit_0.sensor_number == hit_1.sensor_number - 2 or hit_0.sensor_number == hit_1.sensor_number - 1
  # and are_compatible(hit_0, hit_1, max_slope)

# condition = lambda h0, h1: True
condition = classical_condition

number_of_events = 1
total_mc_segments = [0 for _ in range(maximum_hits_in_track)]
reconstructible_mc_segments = [0 for _ in range(maximum_hits_in_track)]
for i in range(number_of_events):
  json_data, event = open_file(i)
  hit_dictionary = {h.id:h for h in event.hits}
  mc_desc = {event.montecarlo['description'][i]:i for i in range(len(event.montecarlo['description']))}
  for p in event.montecarlo['particles']:
    mc_track = p[mc_desc['mcp_hits']]
    if len(mc_track) < maximum_hits_in_track:
      total_mc_segments[len(mc_track)] += len(mc_track) - 1
      # Take particles two by two
      for n in range(len(mc_track)-1):
        h0, h1 = hit_dictionary[mc_track[n]], hit_dictionary[mc_track[n+1]]
        if condition(h0, h1):
          reconstructible_mc_segments[len(mc_track)] += 1
existing_segments = []
for i in range(len(total_mc_segments)):
  if total_mc_segments[i] == 0:
    existing_segments.append(1)
  else:
    existing_segments.append(reconstructible_mc_segments[i] / total_mc_segments[i])

plt.bar([i for i in range(maximum_hits_in_track)][3:], existing_segments[3:], color=default_color)
for rect, label in zip(ax.patches, ['%.2f' % a for a in existing_segments[3:]]):
    height = rect.get_height()
    ax.text(rect.get_x() + rect.get_width()/2, height-0.1, label, ha='center', va='bottom', fontdict={'fontsize': 10, 'family': 'source code pro'})

filename = "single_event/reconstructible.png"



    # if len(mc_track_segments) > 2:
    #   # Get distances between mc hits in the same track
    #   for se0 in mc_track_segments:
    #     for se1 in mc_track_segments:
    #       if se0 != se1:
    #         dist = distance(se0, se1)
    #         if dist < 3:
    #           distances.append(dist)

    #     # Get distances between the hits and any other hit
    #     for se1 in extrapolated_segments:
    #       if se1 not in mc_track_segments:
    #         dist = distance(se0, se1)
    #         if dist < 3:
    #           distances_to_other.append(dist)

# plt.xlabel("Euclidean distances of extrapolated segments of MC tracks\n(wrt other hits in the track)")
# n, bins, patches = plt.hist(distances, 100, normed=0, facecolor=default_color, alpha=0.75)
# n, bins, patches = plt.hist(distances_to_other, 100, normed=0, facecolor=grey_color, alpha=0.75)

# Print whatever plot was created

plt.title(plot_title + " (" + str(number_of_events) + " events)\n")
plt.savefig(foldername + filename)
plt.show()
