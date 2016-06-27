from classical_solver import classical_solver
import event_model as em
import validator_lite as vl
import json

def open_json(event_number):
  f = open("velojson/" + str(event_number) + ".json")
  json_data = json.loads(f.read())
  event = em.event(json_data)
  f.close()
  return json_data, event

def get_normalized_hits(hits, limits):
  n = lambda hit, limits, attribute: \
    (getattr(hit, attribute) + abs(limits[attribute][0])) / (abs(limits[attribute][0]) + abs(limits[attribute][1]))
 
  return [n(hits[0], limits, "x"), n(hits[0], limits, "y"), n(hits[0], limits, "z"), \
    n(hits[1], limits, "x"), n(hits[1], limits, "y"), n(hits[1], limits, "z"), \
    n(hits[2], limits, "x"), n(hits[2], limits, "y"), n(hits[2], limits, "z")]

# # Get an event
# f = open("velojson/1.json")
# json_data = json.loads(f.read())
# event = em.event(json_data)
# f.close()

# # Get all tracks by using the classical method and print them
# print("Invoking classical solver...")
# classical = classical_solver()
# classical_tracks = classical.solve(event)
# print("Found", len(classical_tracks), "tracks")

# Let's just focus on three-hit tracks, and pass the x, y and z coordinate
# x, y and z should be in [0, 1]
# tracks_ghost_list = vl.identify_ghost_tracks(json_data, classical_tracks)

def get_tracks_and_truth(event_number, hit_coord_limits):
  json_data, event = open_json(event_number)
  classical = classical_solver()
  classical_tracks = classical.solve(event)
  three_hit_tracks = [t for t in classical_tracks if len(t.hits) == 3]
  tracks_ghost_list = vl.identify_ghost_tracks(json_data, three_hit_tracks)
  track_input = [get_normalized_hits(t.hits, hit_coord_limits) for t in three_hit_tracks]
  truth = tracks_ghost_list
  return [track_input, truth]

def main():
  hit_coord_limits = {
    "x": (-49.702538, 49.741428),
    "y": (-50.506866, 50.526314),
    "z": (-288.031006, 750.531006)
  }


  number_of_events = 1

  # Let's use several processors to speed this up a little
  from multiprocessing import Pool
  pool = Pool()

  pool_results = [pool.apply_async(get_tracks_and_truth, (i, hit_coord_limits)) for i in range(number_of_events)]
  tracks_truth = [res.get(timeout=None) for res in pool_results]

  # Join in all results
  data = {"tracks": [], "truth": []}
  for temp_tracks, temp_truth in tracks_truth:
    data["tracks"] += temp_tracks
    data["truth"] += temp_truth

  # Print them to a file
  with open('tracks_truth_data.json', 'w') as outfile:
    json.dump(data, outfile)

  # from neurolab import net
  # from neurolab import trans
  # from neurolab import init
  # from neurolab import train
  # from neurolab import error

  # sigmoid = trans.LogSig()
  # ghost_buster = net.newff(minmax=[[0, 1] for _ in range(9)], size=[9, 9, 9], transf=[sigmoid]*3)
  # for l in ghost_buster.layers:
  #   l.initf = init.init_zeros
  # ghost_buster.init()

  # ghost_buster.trainf = train.train_gd
  # ghost_buster.errorf = error.MSE()

if __name__ == '__main__':
  main()
