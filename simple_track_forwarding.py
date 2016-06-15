from classical_solver import classical_solver
import event_model as em
import validator_lite as vl
import json

# Get an event
f = open("velojson/0.json")
json_data = json.loads(f.read())
event = em.event(json_data)
f.close()

# Get all tracks by using the classical method and print them
print("Invoking classical solver...")
classical = classical_solver()
classical_tracks = classical.solve(event)
print("Found", len(classical_tracks), "tracks")

# Validate the event
vl.validate_print([json_data], [classical_tracks])
print('RE long>5GeV, [0-1]:', vl.validate_efficiency([json_data], [classical_tracks], 'long>5GeV'))
print('CF long>5GeV, [0-1]:', vl.validate_clone_fraction([json_data], [classical_tracks], 'long>5GeV'))
print('GF of all tracks, [0-1]:', vl.validate_ghost_fraction([json_data], [classical_tracks]))
