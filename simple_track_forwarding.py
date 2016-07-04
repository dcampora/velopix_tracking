from itertools import combinations
import event_model as em
import matplotlib.pyplot as plt
import json
import math

def max_slope_limit(max_slopes=(0.7, 0.7)):
  def wrapped_function(hit_0, hit_1):
    hit_distance = abs(hit_1[2] - hit_0[2])
    dxmax = max_slopes[0] * hit_distance
    dymax = max_slopes[1] * hit_distance
    return abs(hit_1[0] - hit_0[0]) < dxmax and \
           abs(hit_1[1] - hit_0[1]) < dymax
  return wrapped_function

def sensor_pairs(oddity):
  def wrapped_function(hit_0, hit_1):
    return hit_0.sensor_number == hit_1.sensor_number - 2 and \
           ((hit_0.sensor_number + oddity) % 2) == 0
  return wrapped_function

def slope_within_limits(min_slopes=(0.1, 0.1), max_slopes=(0.2, 0.2)):
  def wrapped_function(hit_0, hit_1):
    hit_distance = abs(hit_1[2] - hit_0[2])
    dxmin = min_slopes[0] * hit_distance
    dymin = min_slopes[1] * hit_distance
    dxmax = max_slopes[0] * hit_distance
    dymax = max_slopes[1] * hit_distance
    xdist = abs(hit_1[0] - hit_0[0])
    ydist = abs(hit_1[1] - hit_0[1])
    return (xdist > dxmin or ydist > dymin) and \
           (xdist < dxmax and ydist < dymax)
  return wrapped_function

def simple_extrapolation(extrapolation_z):
  def wrapped_function(hits):
    tx = (hits[1].x - hits[0].x) / (hits[1].z - hits[0].z)
    ty = (hits[1].y - hits[0].y) / (hits[1].z - hits[0].z)
    x  = hits[0].x + tx * (extrapolation_z - hits[0].z)
    y  = hits[0].y + ty * (extrapolation_z - hits[0].z)
    hit_distance = abs(hits[1][2] - hits[0][2])
    slope = abs(hits[1][0] - hits[0][0]) / hit_distance, abs(hits[1][1] - hits[0][1]) / hit_distance
    return x, y, (hits[0].z + hits[1].z) / 2, slope
  return wrapped_function

def open_file(number):
  f = open("velojson/" + str(number) + ".json")
  json_data = json.loads(f.read())
  event = em.event(json_data)
  f.close()
  return json_data, event

def euclidean_distance(point_0, point_1):
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

def get_segments_from_pairs(event, condition_function, extrapolation_function):
  # Get all pairs of consecutive hits in consecutive sensors
  extrapolated_segments = []
  for s0, s1 in zip(event.sensors[:event.number_of_sensors-2], event.sensors[2:]):
    for h0 in s0:
      for h1 in s1:
        if condition_function(h0, h1):
          extrapolated_segments.append(em.segment([h0, h1], extrapolation_function))
  return extrapolated_segments

def get_mc_tracks(event):
  mc_desc = {event.montecarlo['description'][i]:i for i in range(len(event.montecarlo['description']))}
  mc_tracks = []
  for p in event.montecarlo['particles']:
    hits = p[mc_desc['mcp_hits']]
    hits_list = [event.hit_dictionary[h] for h in hits]
    mc_tracks.append(hits_list)
  return mc_tracks

def get_mc_segments_from_pairs(mc_tracks, condition_function, extrapolation_function):
  extrapolated_segments = []
  for track in mc_tracks:
    track_segments = []
    for i in range(len(track) - 1):
      h0, h1 = track[i], track[i+1]
      if condition_function(h0, h1):
        track_segments.append(em.segment([h0, h1], extrapolation_function))
    if len(track_segments) > 0:
      extrapolated_segments.append(track_segments)
  return extrapolated_segments

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

extrapolation_z = 10000
json_data, event = open_file(1)
hit_dictionary = {h.id:h for h in event.hits}
mc_tracks = get_mc_tracks(event)

start, end, jump = 0, 1, 5
divisor = 100

for sensor_oddity in [0]:
  for i in range(start, end, jump):
    # Some default values for the figure
    fig = plt.figure(figsize=(16, 9))
    ax = plt.axes()
    plt.title("", fontdict={'fontsize': 20, 'family': 'source code pro'})
    plt.xlabel("", fontdict={'family': 'source code pro'})
    plt.ylabel("", fontdict={'family': 'source code pro'})

    extrapolated_segments = get_segments_from_pairs(event, \
      lambda h0, h1: sensor_pairs(sensor_oddity)(h0, h1) and slope_within_limits((i/divisor, i/divisor), ((i+jump)/divisor, (i+jump)/divisor))(h0, h1), \
      simple_extrapolation(extrapolation_z))

    mc_extrapolated_segments = get_mc_segments_from_pairs(mc_tracks, \
      lambda h0, h1: sensor_pairs(sensor_oddity)(h0, h1) and slope_within_limits((i/divisor, i/divisor), ((i+jump)/divisor, (i+jump)/divisor))(h0, h1), \
      simple_extrapolation(extrapolation_z))

    mc_number_of_segments = sum([len(a) for a in mc_extrapolated_segments])

    # We want some statistics about the minimum values to cut,
    # based on some lambda functions to minimize
    functions_minimize = {
      "distance": euclidean_distance,
      "z distance": lambda se0, se1: abs(se0.z - se1.z),
      "x slope": lambda se0, se1: abs(se0.slope[0] - se1.slope[0]),
      "y slope": lambda se0, se1: abs(se0.slope[1] - se1.slope[1])
    }

    # Magic
    cut_limits = {k:[1000.0, 0.0] for k in iter(functions_minimize)}
    for mc_track in mc_extrapolated_segments:
      if len(mc_track) > 1:
        temp_cut_limits = [[1000.0, 0.0] for _ in range(len(functions_minimize))]
        for se0 in mc_track:
          min_limits = [1000.0 for _ in range(len(functions_minimize))]
          for se1 in mc_track:
            if se0 != se1:
              min_limits = list(map(lambda m, f: min(m, f(se0, se1)), min_limits, functions_minimize.values()))
          for temp_cut_limit, min_limit in zip(iter(temp_cut_limits), min_limits):
            # Get min, max for the track
            temp_cut_limit[0] = min(temp_cut_limit[0], min_limit)
            temp_cut_limit[1] = max(temp_cut_limit[1], min_limit)
        for key, temp_cut_limit in zip(iter(functions_minimize), temp_cut_limits):
          # Get min, max for the event
          cut_limits[key][0] = min(cut_limits[key][0], temp_cut_limit[0])
          cut_limits[key][1] = max(cut_limits[key][1], temp_cut_limit[1])

    ## Make histogram plot, tracks hits distance versus non-track hits distance
    # plot_title = "Euclidean distances of extrapolated segments of MC tracks\n" \
    #   + "with condition ("+str(i/divisor)+"), ("+str((i+jump)/divisor)+")\n" \
    #   + "(" + str(mc_number_of_segments) + " / " + str(len(extrapolated_segments)) + " mc segments / extrapolated segments)"
    # distances_to_track_segments, distances_to_any_other_segment = [], []
    # for mc_track in mc_extrapolated_segments:
    #   for n in range(len(mc_track) - 1):
    #     se0, se1 = mc_track[n], mc_track[n+1]
    #     edist = euclidean_distance(se0, se1)
    #     if edist < 6:
    #       distances_to_track_segments.append(edist)
    # for n in range(len(extrapolated_segments) - 1):
    #   se0, se1 = extrapolated_segments[n], extrapolated_segments[n+1]
    #   edist = euclidean_distance(se0, se1)
    #   if edist < 6:
    #     distances_to_any_other_segment.append(edist)
    
    # if len(distances_to_track_segments) > 1 and len(distances_to_any_other_segment) > 1:
    #   n, bins, patches = plt.hist(distances_to_track_segments, 100, normed=0, facecolor=default_color, alpha=0.75)
    #   n, bins, patches = plt.hist(distances_to_any_other_segment, 100, normed=0, facecolor=grey_color, alpha=0.75)

    accept_segments = lambda se0, se1: se0 != se1 \
      and euclidean_distance(se0, se1) < 5.7 \
      and abs(se0.z - se1.z) < 100 \
      and abs(se0.slope[0] - se1.slope[0]) < 0.0032 \
      and abs(se0.slope[1] - se1.slope[1]) < 0.0074

    # Make scatterplot with segments
    plot_title = "Segments with cut requiring three segments with condition\n("+str(i/divisor)+"), ("+str((i+jump)/divisor)+")"
    # Only print extrapolated segments with at least one hit to distance 6 or less
    cut_extrapolated_segments = set()
    # Require at least three segments
    for se0 in extrapolated_segments:
      if se0 not in cut_extrapolated_segments:
        found = False
        for se1 in extrapolated_segments:
          if accept_segments(se0, se1):
            for se2 in extrapolated_segments:
              if accept_segments(se0, se2) and accept_segments(se1, se2):
                cut_extrapolated_segments.add(se0)
                cut_extrapolated_segments.add(se1)
                cut_extrapolated_segments.add(se2)
                found = True
                break
            if found:
              break
    plt.scatter([a.x for a in cut_extrapolated_segments], [a.y for a in cut_extrapolated_segments], color=default_color)
    
    for mc_track_segments in mc_extrapolated_segments:
      temp_mc_track_segments = set()
      # Require at least three segments
      for se0 in mc_track_segments:
        if se0 not in temp_mc_track_segments:
          found = False
          for se1 in mc_track_segments:
            if accept_segments(se0, se1):
              for se2 in mc_track_segments:
                if accept_segments(se0, se2) and accept_segments(se1, se2):
                  temp_mc_track_segments.add(se0)
                  temp_mc_track_segments.add(se1)
                  temp_mc_track_segments.add(se2)
                  found = True
                  break
              if found:
                break
      plt.scatter([a.x for a in temp_mc_track_segments], [a.y for a in temp_mc_track_segments], color=colors[color_id])
      color_id = (color_id + 1) % len(colors)

    # Print whatever plot was created
    plot_title +=  " (" + str(number_of_events) + " events"
    if number_of_events == 1:
      plot_title += ", sensor " + str(sensor_oddity) + ", h#" + str(event.number_of_hits)
    plot_title += ")\n"

    print("Length: " + str(len(extrapolated_segments)))
    print("Min and max for mc tracks:")
    for k, v in iter(cut_limits.items()):
      print(k, v)
    # print("Min and max min_distance within a track: " + str(min_min_distance) + ", " + str(max_min_distance))
    # print("Min and max min_z_distance within a track: " + str(min_max_min_z_distance) + ", " + str(max_max_min_z_distance))
    # print("Min slopes: (" + str(min_min_x_slope) + ", " + str(max_min_x_slope) + "), (" + str(min_min_y_slope) + ", " + str(max_min_y_slope) + ")")

    plt.title(plot_title)
    # plt.show()

    filename = "default.png"
    plt.savefig(filename)
    plt.close()

# plt.show()
