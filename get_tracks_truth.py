import json
from classical_solver import classical_solver
from json import encoder
encoder.FLOAT_REPR = lambda o: format(o, '.3f')

def get_normalized_hits(hits, limits):
  n = lambda hit, limits, attribute: \
    (getattr(hit, attribute) + abs(limits[attribute][0])) / (abs(limits[attribute][0]) + abs(limits[attribute][1]))
 
  return [n(hits[0], limits, "x"), n(hits[0], limits, "y"), n(hits[0], limits, "z"), \
    n(hits[1], limits, "x"), n(hits[1], limits, "y"), n(hits[1], limits, "z"), \
    n(hits[2], limits, "x"), n(hits[2], limits, "y"), n(hits[2], limits, "z")]

def get_tracks_and_truth(event_number, hit_coord_limits, container_folder="velojson/"):
  try:
    json_data, event = open_json_event(event_number, container_folder)
    classical = classical_solver()
    classical_tracks = classical.solve(event)
    three_hit_tracks = [t for t in classical_tracks if len(t.hits) == 3]
    if len(three_hit_tracks) > 0:
      tracks_ghost_list = vl.identify_ghost_tracks(json_data, three_hit_tracks)
      track_input = [get_normalized_hits(t.hits, hit_coord_limits) for t in three_hit_tracks]
      truth = tracks_ghost_list
      return [track_input, truth]
    else:
      return [[], []]
  except e:
    print(e)
    return [[], []]

def get_training_data(number_of_events=100, container_folder="velojson/"):
  hit_coord_limits = {
    "x": (-49.702538, 49.741428),
    "y": (-50.506866, 50.526314),
    "z": (-288.031006, 750.531006)
  }

  # Let's use several processors to speed this up a little
  from multiprocessing import Pool
  pool = Pool()

  pool_results = [pool.apply_async(get_tracks_and_truth, (i, hit_coord_limits, container_folder)) \
    for i in range(number_of_events)]
  tracks_truth = [res.get(timeout=None) for res in pool_results]

  # Join in all results
  data = {"tracks": [], "truth": []}
  for temp_tracks, temp_truth in tracks_truth:
    data["tracks"] += temp_tracks
    data["truth"] += temp_truth

  # Print them to a file
  with open('tracks_truth_data.json', 'w') as outfile:
    json.dump(data, outfile)
