from classical_solver import classical_solver
import event_model as em
import validator_lite as vl
import json
from json import encoder
encoder.FLOAT_REPR = lambda o: format(o, '.3f')

def open_json_event(event_number, container_folder="velojson/"):
  f = open(container_folder + str(event_number) + ".json")
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
  except Exception, e:
    print(e)
    return [[], []]

def main(number_of_events=100, container_folder="velojson/"):
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


def ghost_buster(json_file):
  f = open(json_file)
  json_data = json.loads(f.read())
  f.close()

  from neurolab import net
  from neurolab import trans
  from neurolab import init
  from neurolab import train
  from neurolab import error
  import numpy as np

  sigmoid = trans.LogSig()
  gb_sizes = [9, 9, 9, 9, 1]
  gb = net.newff(minmax=[[0, 1] for _ in range(9)], size=gb_sizes, transf=[sigmoid]*len(gb_sizes))
  # for l in gb.layers:
  #   l.initf = init.init_zeros
  gb.init()

  gb.trainf = train.train_gd
  gb.errorf = error.MSE()

  net_input = np.array(json_data["tracks"])
  net_truth_input = np.array([[a] for a in json_data["truth"]])

  # Train the network
  sim0 = gb.sim(net_input)
  error0 = gb.errorf(net_truth_input, sim0)
  print("Starting error:", error0)
  gb.train(net_input, net_truth_input, epochs=500, show=20, goal=0.001)
  sim1 = gb.sim(net_input)
  error1 = gb.errorf(net_truth_input, sim1)
  print("Finishing error:", error1)
  
  for i in range(len(sim1)):
    print(training_set["truth"][i], sim1[i])


if __name__ == '__main__':
  # ghost_buster("tracks_truth_data.json")
  main()
