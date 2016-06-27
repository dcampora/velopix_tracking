from classical_solver import classical_solver
import event_model as em
import validator_lite as vl
import json

# Get an event
f = open("velojson/1.json")
json_data = json.loads(f.read())
event = em.event(json_data)
f.close()

# Get all tracks by using the classical method and print them
print("Invoking classical solver...")
classical = classical_solver()
classical_tracks = classical.solve(event)
print("Found", len(classical_tracks), "tracks")

# Validate the event
# vl.validate_print([json_data], [classical_tracks])
# print('RE long>5GeV, [0-1]:', vl.validate_efficiency([json_data], [classical_tracks], 'long>5GeV'))
# print('CF long>5GeV, [0-1]:', vl.validate_clone_fraction([json_data], [classical_tracks], 'long>5GeV'))
# print('GF of all tracks, [0-1]:', vl.validate_ghost_fraction([json_data], [classical_tracks]))

# Let's look at the data
tracks_ghost_list = vl.identify_ghost_tracks(json_data, classical_tracks)
d = {"length": [], "chi2": [], "interleave": [], "accept": []}
for track, is_ghost in zip(classical_tracks, tracks_ghost_list):
  d["length"].append(track.length())
  d["chi2"].append(track.chi2())
  d["interleave"].append(track.interleaved_sensors_relative())
  d["accept"].append(is_ghost)

# print(d)
print("Length   chi2   interleave   accept")
for i in range(len(d["length"])):
  print("%2d" % d["length"][i], \
    "%1.4f" % d["chi2"][i], \
    "%1.2f" % d["interleave"][i], \
    d["accept"][i])
